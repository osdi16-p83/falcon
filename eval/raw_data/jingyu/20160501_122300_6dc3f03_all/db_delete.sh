#!/bin/bash

if [ -f ~/.bashrc ]; then
  source ~/.bashrc
fi

ssh -f $LOGNAME@$(cat $RDMA_ROOT/apps/env/local_host) "sudo rm -rf ~/.db"
ssh -f $LOGNAME@$(cat $RDMA_ROOT/apps/env/remote_host1) "sudo rm -rf ~/.db"
ssh -f $LOGNAME@$(cat $RDMA_ROOT/apps/env/remote_host2) "sudo rm -rf ~/.db"
