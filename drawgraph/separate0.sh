#!/bin/bash
HADOOP_HOME="/home/yuyuzhou/Hadoop/hadoop-2.6.0"
rm -rf $HADOOP_HOME/output
numactl -N 0 -m 0 strace -s 256 -o ~/data/hadoop_w_full.data -CTf numactl -N 0 -m 0 $HADOOP_HOME/bin/hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.6.0.jar grep $HADOOP_HOME/input $HADOOP_HOME/output '[a-z.]+'
