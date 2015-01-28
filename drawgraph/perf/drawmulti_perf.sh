#!/bin/bash 
for i in 1 2 4 8
do
    data=data_mmap_perf_1v${i}
    for sys in mmap munmap
    do
        sh -x drawgraph_perf.sh $data $sys
        mv out_${sys} out_${sys}.${data}.2.1
    done
done
