#!/bin/bash
for i in 1 2 4 8
do
    sh -x mmapcase_perf.sh $i
done
