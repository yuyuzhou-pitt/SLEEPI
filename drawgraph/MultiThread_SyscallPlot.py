#!/usr/bin/python

import sys, getopt
import operator
import ntpath
import math
import pdb

def calcTime(line, sumSec, sysSec, histodata):
    usecs = 1000000
    timelist = []
    
    if "resumed" in line:
        item = line.split(" ", 2)[1]
        elapse = line[-10:-2]
    else:
        item = line.split('(')[0]
        elapse = line[-10:-2]

    if elapse[0].isdigit():
        sumSec += float(elapse)
        # for the general table
        if item in sysSec:
            sysSec[item][0] += float(elapse) #sum
            if sysSec[item][1] < float(elapse):
                sysSec[item][1] = float(elapse) #max
            if sysSec[item][2] > float(elapse):
                sysSec[item][2] = float(elapse) #min
            sysSec[item][3] += (float(elapse) * usecs) ** 2 #paritail result
        else:
            timelist.append(float(elapse)) # sum
            timelist.append(float(elapse)) # max
            timelist.append(float(elapse)) # min
            timelist.append((float(elapse) * usecs) ** 2) # sd partial result
            sysSec[item] = timelist

        # for the histograph table
        if item in histodata:
            histodata[item].append(float(elapse))
    return sumSec, sysSec, histodata

def updateTable(line, sumSec, sysSec, outTable):
    usecs = 1000000
    items = []
    cols = line.split()
    #pdb.set_trace()
    if len(cols) == 5:
        outkey = cols[4] #syscall
        error = 0
    elif len(cols) == 6:
        outkey = cols[5] #syscall
        error = cols[4] #errors

    if outkey not in outTable:
        if outkey in sysSec:
            percent = sysSec[outkey][0] / sumSec
            items.append(percent)
            items.append(sysSec[outkey][0])
            items.append(int((sysSec[outkey][0])*usecs)/int(cols[3])) #usecs/call
            items.append(sysSec[outkey][1]*usecs) #max
            items.append(sysSec[outkey][2]*usecs) #min
            items.append((sysSec[outkey][3]/(int(cols[3])) - ((int((sysSec[outkey][0])*usecs) /int(cols[3]))**2))**0.5)
            items.append(cols[3]) #calls
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
        #pdb.set_trace()
        if histoW != 0:
            span = histoW / 1000000.0
        print("Using span: %f." % span)

        startN = 1
        if sysSec[histo][2] > span:
            startN = math.ceil(sysSec[histo][2]/span) #  min/span

        widthN = (histoN * 2)/3
        expData = (widthN + startN - 1) * span
        sysHisto = initSysHisto(sysHisto, span, histoW, histoN, expIndex, max(sysSec[histo][1], sysSec2[histo][1]), min(sysSec[histo][2], sysSec2[histo][2]) )
        for data in histodata[histo]:
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
    outputFP.write("{:11s}{:11s}{:11s}{:10s}{:10s}{:19s}{:4s}{:6s}{:7s}\t{:20s}\n"
                   .format('SUMMARY:', '%_time', 'seconds', 'ave.us', 'max.us', 'min.us', 
                   'sd', 'calls', 'errors', 'syscall'))
    for key, val in sortedTable:
         outputFP.write("{:11s}{:6.2f}{:12.6f}{:10d}{:10d}{:10d}{:15.2f}{:7d}{:7d}\t{:20s}\n"
                        .format('SUMMARY:', val[0]*100, val[1], int(val[2]), int(val[3]), 
                        int(val[4]),val[5], int(val[6]), int(val[7]), val[8]))

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
        if line[0].isdigit() and not line.endswith("total\n"):
            line = line[6:] # trim the starting 4 digits
        if line[0].isalpha() or line[0] == '<': # line is "<... futex resumed> ..."
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
            
    outputFP = open(outputFile, 'w')
    for line in inputFP:
        if line[0].isdigit() and not line.startswith("100") and not line.endswith("total\n"):
            #line = line.split("  ", 1)[1] # trim the starting 4 digits
            line = line[6:] # trim the starting 4 digits
            #print(line)
        if line[0].isalpha() or line[0] == '<': # line is "<... futex resumed> ..."
            sumSec, sysSec, histodata = calcTime(line, sumSec, sysSec, histodata)
        elif (line[0] == ' ' or line[0] == '1') and not line.endswith("total\n"):
            outTable = updateTable(line, sumSec, sysSec, outTable)
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
    print 'i.e: SyscallPlot.py -d \"futex poll\" -w 100 -n 30 -i cassandra_all.data -o cassandra_all.data.out'

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
