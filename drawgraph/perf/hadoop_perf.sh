#!/bin/bash
export JAVA_HOME=/usr/lib/jvm/java
HADOOP_PREFIX=/home/yuyuzhou/Hadoop/hadoop-2.6.0
HADOOP_HOME="/home/yuyuzhou/Hadoop/hadoop-2.6.0"
rm -rf $HADOOP_HOME/output
time numactl -N 0 -m 0 perf trace -o hadoop_perf.perf -- numactl -N 0 -m 0 $HADOOP_HOME/bin/hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-2.6.0.jar grep $HADOOP_HOME/input $HADOOP_HOME/output '[a-z.]+'
