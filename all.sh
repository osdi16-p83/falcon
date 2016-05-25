#!/bin/sh
# Author: Jingyu
# Date: April 19


set -x

RDMA_NUM=0.0.4
RDMA_ENABLED=true
#Build_list="redis ssdb mongodb"
Build_list="redis"


RDMA_VERSION=v${RDMA_NUM}
RDMA_TAR=${RDMA_VERSION}.tar.gz
RDMA_URL="https://github.com/wangchenghku/RDMA_Paxos/archive/$RDMA_TAR"

if [ ! -f "$RDMA_TAR" ]; then
	curl -L -O "$RDMA_URL" 
fi

# dir name RDMA_Paxos-0.0.3
RDMA_OUTPUT_DIR=RDMA_Paxos
if [ ! -d "$RDMA_OUTPUT_DIR" ]; then
	rm -rf $RDMA_OUTPUT_DIR
	mkdir -p $RDMA_OUTPUT_DIR
	tar -xf $RDMA_TAR -C $RDMA_OUTPUT_DIR --strip-components=1
fi

cd $RDMA_OUTPUT_DIR
pwd

RDMA_CODE_DIR=RDMA
cd $RDMA_CODE_DIR

# make deps
./mk

# make RDMA code
RDMA_TARGET_DIR=target
cd $RDMA_TARGET_DIR

make
cd ../ # back to RDMA
cd ../ # back to Root


# update env
cd apps
cd env # root/apps/env
sh ./local_env.sh
sh ./remote_env.sh

# build Redis
cd ../ # root/apps

source ~/.bashrc
for item in $Build_list
do
	cd $item
	if [ "$RDMA_ENABLED" = true ]; then	
		sh ./hook-mk
	else
		sh ./mk
	fi
	cd ../ 
done

cd ../ # root
cd eval

for item in $Build_list
do
	if [ "$RDMA_ENABLED" = true ]; then
		CFG_NAME=${item}-hook.cfg
	else
		CFG_NAME=${item}.cfg
	fi 
	python ./eval.py -f  $CFG_NAME	
done
