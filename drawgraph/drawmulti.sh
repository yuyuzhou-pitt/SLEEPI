#!/bin/bash 
for i in 1 2 4 8 16 32
do
    data=data_readtest_sleep_56s_1v${i}
    for sys in read
    do
        sh -x drawgraph.sh $data $sys
        mv out_${sys} out_${sys}.${data}.1.1
    done
done
