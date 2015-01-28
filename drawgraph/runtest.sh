#!/bin/bash

TEMPFILE=.runsenarioes.sh

cat <<EOF > $TEMPFILE
#!/bin/bash
#==Hadoop==
#==Senario 1: Seperate(1 on node 0, then 1 on node 1)==
sh ~/Hadoop/hadoop-2.6.0/separate0.sh
sh ~/Hadoop/hadoop-2.6.0/separate1.sh
#==Senario 2: Concurrent(2 hadoop, 1 on node 0, 1 on node 1)==
sh ~/Hadoop/hadoop-2.6.0/cur2.sh
#==Senario 3: Concurrent(4 hadoop, 2 on node 0, 2 on node 1)==
sh ~/Hadoop/hadoop-2.6.0/curN.sh
#==Cassandra==
sh ~/Cassandra/node0.sh
sh ~/Cassandra/node1.sh
sh ~/Cassandra/all.sh
#==Graphlab==
sh ~/graphlab/separate.sh
sh ~/graphlab/cur2.sh
sh ~/graphlab/cur4.sh
EOF

# run above senarioes
sh $TEMPFILE
# draw graph based on data
sh ~/scripts/drawgraph.sh
mv ~/data ~/data_no_background
mv ~/out ~/out_no_background
mkdir -p ~/data

# NOTE: backup ~/out, and then run this script again with noise (e.g. building kernel)
# build kernel
cd ~/scripts/linux-3.11.7
numactl -N 0 -m 0 make &

# run senaroes again
sh $TEMPFILE
sh ~/scripts/drawgraph.sh
mv ~/data ~/data_with_background
mv ~/out ~/out_with_background

# clean the temp file
rm $TEMPFILE
