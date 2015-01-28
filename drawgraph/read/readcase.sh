#!/bin/bash
N=4 # how many tasks on each node
if [ "x"$1 != "x" ]; then
N=$1
fi
PROG=./readtest
NOISE=./readnoise
TARGETDIR=data_readtest_sleep_56s_1v${N}

mkdir -p $TARGETDIR
#== Senario 1 Step 1: single ==
numactl -N 0 -m 0  strace -o $TARGETDIR/read_other_wo.data -e trace=desc -TCf numactl -N 0 -m 0 $PROG
#== Senario 1 Step 2: with noise on the other numa node ==
for ((i=0;i<N;i++));do
    numactl -N 1 -m 1 $NOISE &
done
numactl -N 0 -m 0  strace -o $TARGETDIR/read_other_w.data -e trace=desc -TCf numactl -N 0 -m 0 $PROG &
wait
