#!/usr/bin/python
# This file will deal with output from perf trace. Such as:
#     0.000 ( 0.000 ms):  ... [continued]: read()) = 1
#     0.186 ( 0.000 ms):  ... [continued]: execve()) = -2
#     0.207 ( 0.017 ms): execve(arg0: 140736568868063, arg1: 140736568879728, arg2: 39100464, arg3: 140736568867664, arg4: 7310027616929870437, arg5: 140736568867912) = -2
#     1.304 ( 1.093 ms): execve(arg0: 140736568868064, arg1: 140736568879728, arg2: 39100464, arg3: 140736568867664, arg4: 7310027616929870437, arg5: 140736568867912) = 0
#     1.378 ( 0.005 ms): brk(                                                                  ) = 0x9d0000
#     1.434 ( 0.010 ms): mmap(len: 4096, prot: READ|WRITE, flags: PRIVATE|ANONYMOUS, fd: -1    ) = 0xb3775000
#     1.479 ( 0.017 ms): access(filename: 0x37ccc1db60, mode: R                                ) = -1 ENOENT No such file or directory

import sys, getopt
import operator
import ntpath
import math
import pdb
import re

def calcTime(line, sumSec, sysSec, histodata):
    usecs = 1000000.0
    msecs = 1000.0
    timelist = []
    
    cols = line.split(':')
    if "continued" in line:
        item = cols[2].split('(')[0].strip()
        #elapse = (cols[0].split('(')[1].split(')').split()[0])*msecs
    else:
        item = cols[1].split('(')[0].strip()
    #pdb.set_trace()
    #elapse = re.search(r"\(([0-9.]+)\)", cols[0])
    elapse = float(re.search(r"([0-9.]+)", cols[0].split('(')[1]).group(1))
    elapse /= msecs # change to s
    # filter the abnormal data if it's too big (larger than msecs)
    if elapse > msecs:
        return sumSec, sysSec, histodata

    #pdb.set_trace()
    sumSec += elapse
    #if item == "futex":
    #    print elapse
    # for the general table
    if item in sysSec:
        sysSec[item][0] += elapse #sum
        if sysSec[item][1] < elapse:
            sysSec[item][1] = elapse #max
        if sysSec[item][2] > elapse:
            sysSec[item][2] = elapse #min
        sysSec[item][3] += (elapse * usecs) ** 2 #paritail result
        sysSec[item][4] += 1 # number of calls
    else:
        timelist.append(elapse) # sum
        timelist.append(elapse) # max
        timelist.append(elapse) # min
        timelist.append((elapse * usecs) ** 2) # sd partial result
        timelist.append(1) # number of calls
        sysSec[item] = timelist

    # for the histograph table
    if item in histodata:
        histodata[item].append(elapse)

    return sumSec, sysSec, histodata

def updateTable(sumSec, sysSec, outTable):
    usecs = 1000000
    for outkey in sysSec:
        items = []
        error = '-' # error is not availible in perf trace output

        if outkey not in outTable:
            percent = sysSec[outkey][0] / sumSec
            items.append(percent)
            items.append(sysSec[outkey][0])
            items.append(int((sysSec[outkey][0])*usecs)/int(sysSec[outkey][4])) #usecs/call
            items.append(sysSec[outkey][1]*usecs) #max
            items.append(sysSec[outkey][2]*usecs) #min
            items.append((sysSec[outkey][3]/(int(sysSec[outkey][4])) - 
                          ((int((sysSec[outkey][0])*usecs) /int(sysSec[outkey][4]))**2))**0.5)
            items.append(sysSec[outkey][4]) #calls
            items.append(error)
            items.append(outkey)

            outTable[outkey] = items
        else:
            print("duplicated syscall name: %s" % outkey)

    return outTable

def initSysHisto(sysHisto, span, histoW, histoN, expIndex, rangeMax, rangeMin):
    startN = 1
    if rangeMin > span:
        startN = math.ceil(rangeMin/span) #  min/span
    key = startN * span
    curN = startN
    widthN = (histoN * 2)/3
    while key < rangeMax + span: # key < max + span
        key0 = key - span + 0.000001

        if histoW != 0 and curN > widthN + startN - 1: # use expIndex after width
            span = span * expIndex

        fullkey = "%s~%s" %("{:f}".format(key0), "{:f}".format(key))
        curN += 1
        key += span

        sysHisto[fullkey] = 0

    return sysHisto

def histoTable(sysSec, sysSec2, histodata, histoW, histoN, expIndex, outHisto):
    for histo in histodata:
        sysHisto = {}
        span = (max(sysSec[histo][1], sysSec2[histo][1]) - min(sysSec[histo][2], sysSec2[histo][2]))/histoN # span = (max - min)/number
        if histoW != 0:
            span = histoW / 1000000.0
        print("Using span: %f." % span)

        startN = 1
        if sysSec[histo][2] > span: # min > span
            startN = math.ceil(sysSec[histo][2]/span) #  min/span

        widthN = (histoN * 2)/3
        expData = (widthN + startN - 1) * span
        #pdb.set_trace()
        sysHisto = initSysHisto(sysHisto, span, histoW, histoN, expIndex, 
                   max(sysSec[histo][1], sysSec2[histo][1]), min(sysSec[histo][2], sysSec2[histo][2]) )
        for data in histodata[histo]:
            if data <= 0:
                continue
            if histoW != 0 and data > expData:
                expSpan = span
                key = expData + span
                while data > key:
                    expSpan = expSpan * expIndex 
                    key = key + expSpan
                key0 = key - expSpan + 0.000001
            else:
                NN = math.ceil(float(data)/span)
                key = NN * span
                key0 = key - span + 0.000001
 
            fullkey = "%s~%s" %("{:f}".format(key0), "{:f}".format(key))
            #print("data=%f, fullkey=%s" % (data, fullkey))
            if fullkey in sysHisto:
                sysHisto[fullkey] += 1 # accumulating
            else:
                sysHisto[fullkey] = 1 # initial value

        outHisto[histo] = sysHisto

    return outHisto

def writeTable(outTable, outputFP):
    sortedTable = sorted(outTable.items(), key=operator.itemgetter(1), reverse=True)
    outputFP.write("{:11s}{:11s}\t{:11s}\t{:10s}\t{:10s}\t{:19s}\t{:4s}\t{:6s}\t{:7s}\t{:20s}\n"
                   .format('SUMMARY:', '%_time', 'seconds', 'ave.us', 'max.us', 'min.us', 
                   'sd', 'calls', 'errors', 'syscall'))
    for key, val in sortedTable:
         outputFP.write("{:11s}{:6.2f}\t{:12.6f}\t{:10d}\t{:10d}\t{:10d}\t{:15.2f}\t{:7d}\t{:7s}\t{:20s}\n"
                        .format('SUMMARY:', val[0]*100, val[1], int(val[2]), int(val[3]), 
                        int(val[4]),val[5], int(val[6]), val[7], val[8]))

def writeHisto(outHisto, outputFP):
    outputFP.write("{:12s}{:12s}{:12s}\t{:12s}\n" .format('HISTO:', 'syscall', 'times', 'seconds'))
    for keyT, valT in outHisto.items():
        sortedTable = sorted(valT.items(), key=operator.itemgetter(0), reverse=False)
        #print(sortedTable)
        for item in sortedTable:
            outputFP.write("{:12s}{:12s}{:10d}\t{:12s}\n" .format('HISTO:', keyT, item[1], item[0]))

def inputFile2(inputFile):
    #pdb.set_trace()
    w_or_wo = "_" + inputFile.split('/')[-1].split('.')[0].split('_')[-1] + "."
    if w_or_wo == "_wo.":
        w_replace = "_w."
    else:
        w_replace = "_wo."

    return inputFile.replace(w_or_wo, w_replace)

def getMaxMin(inputFile, sysCall):
    sumSec = 0.0
    sysSec = {}
    histodata = {}
    for sc in sysCall:
        histodata[sc] = []

    inputFP2 = open(inputFile, 'r')
    for line in inputFP2:
        if not line.strip():
            continue
        if line.split()[0][0].isdigit(): # when line is not in summary area
            sumSec, sysSec, histodata = calcTime(line, sumSec, sysSec, histodata)
    return sysSec

def summary(inputFile, outputFile, sysCall, histoW, histoN, expIndex):   
    #pdb.set_trace()
    sumSec = 0.0
    sysSec = {}
    sysSec2 = {}
    outTable = {}
    histodata = {}
    for sc in sysCall:
        histodata[sc] = []

    inputFP = open(inputFile, 'r')
    if "_w" in inputFile:
        sysSec2 = getMaxMin(inputFile2(inputFile), sysCall)
    else:
        print "input file name should contain '_w'."
        return -1
            
    outputFP = open(outputFile, 'w')
    for line in inputFP:
        if not line.strip():
            continue
        #pdb.set_trace()
        try:
            if line.split()[0][0].isdigit(): # when line is not in summary area
                sumSec, sysSec, histodata = calcTime(line, sumSec, sysSec, histodata)
        except:
            print "line=%s.\n" % line
            print "Unexpected error:", sys.exc_info()[0]
            raise

    outTable = updateTable(sumSec, sysSec, outTable)
    writeTable(outTable, outputFP)

    # for histograph
    outHisto = {}
    #print("%d lines wrote." % histoN)
    outHisto = histoTable(sysSec, sysSec2, histodata, histoW, histoN, expIndex, outHisto)
    # use exponential increasing width
    #outHisto = expWidth(outHisto, histoW, histoN)
    writeHisto(outHisto, outputFP)

def help():
    print 'Usage: SyscallPlot.py [-h/--help] [-s/--syscall <syscall-list>] [-n/--number]'
    print '                      [-w/--width] [-n/--number]'
    print '                      -i <inputfile> -o <outputfile>'
    print '       [-s/--syscall <syscall-list>]: the syscall(s) to draw histograph, devided by space'
    print '                                      default is \"futex\"'
    print '       [-w/--width]: statistic width in us, default is 100. Set to 0 if not using'
    print '       [-n/--number]: division numbers, default is 30. Use average division if width is 0. '
    print '                      If width is not 0, the first 2/3 will use this width and the rest '
    print '                      width will be exponential increasing. The final number will be various.'
    print '                      e.g.: if width is 100 and number is 30, the first 20 will use width 100,'
    print '                      and 21 will use 1000, 22 will use 10000, and so on until to the end.'
    print '       -i <inputfile>: input data'
    print '       -o <outputfile>: output for bargraph.pl'
    print 'i.e: SyscallPlot.py -s \"futex poll\" -w 100 -n 30 -i cassandra_all.data -o cassandra_all.data.out'

def main(argv):
    inputFile = ''
    outputFile = ''
    sysCall = ['futex'] # draw histograph for futex by default 
    histoW = 100 # statistic width in us, it overrides -n/--number when specified
    histoN = 30 # how many bars for the x-axis
    expIndex = 2 # the exponential index
    try:
       opts, args = getopt.getopt(argv, "hs:n:w:i:o:", ["syscall=", "number=", "width=", "ifile=", "ofile="])
    except getopt.GetoptError:
       print 'Incorrect command format'
       help()
       sys.exit(2)
    if len(opts) == 0:
       print 'Insufficient arguments'
       help()
       sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            help()
            sys.exit()
        elif opt in ("-s", "--syscall"):
            sysCall = arg.split()
        elif opt in ("-w", "--width"):
            histoW = int(arg)
        elif opt in ("-n", "--number"):
            histoN = int(arg)
        elif opt in ("-i", "--ifile"):
            inputFile = arg
        elif opt in ("-o", "--ofile"):
            outputFile = arg

    summary(inputFile, outputFile, sysCall, histoW, histoN, expIndex)

if __name__ == "__main__":
    main(sys.argv[1:])
