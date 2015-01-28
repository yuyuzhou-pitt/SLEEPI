#!/bin/bash
# Before executing:
# 1. Set DATA, OUT for data source and output directory
# 2. Set LINEFROM and LINETO to decide which lines to be used for drawing
# 3. Set GRAPHFORMAT, GRAPHTYPE and GRAPHSIZE for graph format, type and size

#==== Configuration ====
DATA=mmap0_data_1v2 # data source
DATABAK=.mmap_data.bak
OUT=out # output directory
GRAPH=HISTO # draw histograph by default
SYSCALL=futex
RUNPLOT=y
HISTOW=2 # statistic width in us. Set 0 if not using, or it overrides -n/--number.
HISTON=200 # division numbers. Overridden by HISTOW when it is not 0.
LINEFROM=1 # which line to start (ignoring the head line)
LINENUM=50 # till EOF if not set
GRAPHFORMAT=./bargraph_format.perf # the bargraph format file
GRAPHTYPE=png # eps/ppm/png (latex/bitmap/slides)
GRAPHSIZE=700x700

if [ "$1" != "" ]; then
    DATA=$1
fi

if [ "$2" != "" ]; then
    SYSCALL=$2
fi

#==== SyscallPlot.py confirmation ====
#if [ "xy" != x$RUNPLOT ]; then
#read -p "[OPTIONAL] Run SyscallPlot.py to create *.out again? [y/N]" -n 1 -r
#echo    # (optional) move to a new line
#if [[ $REPLY =~ ^[Yy]$ ]]
#then
    #==== clean and bakeup directory ====
    if [ -d "$OUT" ]; then mv ${OUT} ${OUT}.`date +%Y%m%d_%H%M`;fi
    mkdir $OUT;
    if [ -d "$DATABAK" ]; then rm -rf $DATABAK; fi
    
    printf "Backuping ${DATA}... "
    cp -rf $DATA $DATABAK
    printf "DONE!\n"
    
    #==== execute SyscallPlot.py ====
    printf "Executing SyscallPlot.py. It takes several seconds, please wait... \n"
    for data in `ls -d1 ${DATABAK}/*.data`; do
        printf "python MultiThread_SyscallPlot.py -w ${HISTOW} -n ${HISTON} -s ${SYSCALL} -i ${data} -o ${data}.out\n"
        python MultiThread_SyscallPlot_perf.py -w ${HISTOW} -n ${HISTON} -s ${SYSCALL} -i ${data} -o ${data}.out > /dev/null 2>&1
        printf "cp ${data}.out ${OUT}\n"
        cp ${data}.out ${OUT}
    done
    printf "DONE SyscallPlot.py!\n"
#fi

#==== draw bargraph ====
if [ ! -d "$OUT" ]; then 
    printf "ERROR: '$OUT' not found. Please answer 'Y/y' to run SyscallPlot.py again.\n"
    exit
fi
printf "Start drawing bargraph... \n"
# grab data from output for bargraph
for file in `ls -d1 ${OUT}/*.out`; do
    cat ${GRAPHFORMAT} > ${file}.perf
    if [ "x" = x${LINENUM} ] ; then LINENUM=10000; fi
    #LINENUM=$((${LINETO} - ${LINEFROM} + 1))
    LINETO=$((${LINENUM} + ${LINEFROM} + 1))
    printf "LINETO=$LINENUM\n"
    cat ${file} | grep ${GRAPH} | grep -v 'syscall' | head -n${LINETO} | tail -n${LINENUM} | awk '{print $NF, $3}' >> ${file}.perf
    printf "Drawing bargarph to ${file}.${GRAPHTYPE}\n"
    if [ "xeps" = x${GRAPHTYPE} ]; then
        bargraph/bargraph.pl -fig ${file}.perf > ${file}.${GRAPHTYPE}
    elif [ "xppm" = x${GRAPHTYPE} ] || [ "xpng" = x${GRAPHTYPE} ]; then
        bargraph/bargraph.pl -fig ${file}.perf | fig2dev -L ${GRAPHTYPE} -m 4 > ${file}.${GRAPHTYPE}
        mogrify -reverse -flatten ${file}.${GRAPHTYPE}
        mogrify -resize ${GRAPHSIZE} -format png ${file}.${GRAPHTYPE}
    else
        printf "ERROR: Invalid GRAPHTYPE: ${GRAPHTYPE}. Please try again.\n"
        exit
    fi
done
printf "DONE Drawing!\n"

#==== clean up ====
rm -rf $DATABAK
rm -rf ${OUT}/*.perf
rm -rf ${OUT}_$SYSCALL
mv ${OUT} ${OUT}_$SYSCALL
#rm -rf ${OUT}/*.out
