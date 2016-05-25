#!/bin/bash

#clamav modify
ssh 10.22.1.1 "sed -i 's/MaxThreads $1/MaxThreads $2/g' $RDMA_ROOT/apps/clamav/clamd.conf"
ssh 10.22.1.2 "sed -i 's/MaxThreads $1/MaxThreads $2/g' $RDMA_ROOT/apps/clamav/clamd.conf"
ssh 10.22.1.3 "sed -i 's/MaxThreads $1/MaxThreads $2/g' $RDMA_ROOT/apps/clamav/clamd.conf"

#mediatomb modify
sed -i "s/-c $1/-c $2/g" mediatomb-output.cfg
sed -i "s/-c $1/-c $2/g" mediatomb-origin.cfg

#memcached modify
sed -i "s/--num-conns=$1/--num-conns=$2/g" memcached-origin.cfg
sed -i "s/--num-conns=$1/--num-conns=$2/g" memcached-output.cfg

#mongodb modify
sed -i "s/-threads $1/-threads $2/g" mongodb-origin.cfg
sed -i "s/-threads $1/-threads $2/g" mongodb-output.cfg

#mysql modify
sed -i "s/--num-threads=$1/--num-threads=$2/g" mysql-origin.cfg
sed -i "s/--num-threads=$1/--num-threads=$2/g" mysql-output.cfg

#redis modify
sed -i "s/-c $1/-c $2/g" redis-output.cfg
sed -i "s/-c $1/-c $2/g" redis-origin.cfg

#ssdb modify
sed -i "s/28888 4500 $1/28888 4500 $2/g" ssdb-origin.cfg
sed -i "s/28888 4500 $1/28888 4500 $2/g" ssdb-output.cfg

#ldap modify
sed -i "s/-c $1 -m $1/-c $2 -m $2/g" ldap-origin.cfg
sed -i "s/-c $1 -m $1/-c $2 -m $2/g" ldap-output.cfg

