#!/bin/sh

PS_CMD="ps -elf| grep redis-server | grep -v grep; sudo netstat -nlpt | grep 7004; sudo ifconfig eth4"
ssh hkucs-PowerEdge-R430-1 $PS_CMD 
ssh hkucs-PowerEdge-R430-2 $PS_CMD 
ssh hkucs-PowerEdge-R430-3 $PS_CMD 

