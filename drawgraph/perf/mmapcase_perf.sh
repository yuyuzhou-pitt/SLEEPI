#!/bin/bash
N=4 # how many tasks on each node
if [ "x"$1 != "x" ]; then
N=$1
fi
PROG=./mmaptest
NOISE=./mmapnoise
TARGETDIR=data_mmap_perf_1v${N}

mkdir -p $TARGETDIR
#== Senario 1 Step 1: single ==
numactl -N 0 -m 0 perf trace -T -o $TARGETDIR/mmaptest_wo.perf -- numactl -N 0 -m 0 $PROG
#== Senario 1 Step 2: with noise on the other numa node ==
for ((i=0;i<N;i++));do
    numactl -N 1 -m 1 $NOISE &
done
numactl -N 0 -m 0 perf trace -T -o $TARGETDIR/mmaptest_w.perf -- numactl -N 0 -m 0 $PROG &
wait
