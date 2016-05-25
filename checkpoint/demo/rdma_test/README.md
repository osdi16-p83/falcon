## Mellanox OFED for Linux Installation
  
1. Download MLNX_OFED at http://www.mellanox.com/page/products_dyn?product_family=26&mtag=linux_sw_drivers.  
2. Login to the installation machine as root.  
3. Mount the ISO image on your machine `mount -o ro,loop MLNX_OFED_LINUX-<ver>-<OS label>.iso /mnt`.  
4. Run the installation script `/mnt/mlnxofedinstall --without-fw-update`.  
5.  Run the `/usr/bin/hca_self_test.ofed` utility to verify whether or not the InfiniBand link is up.  
  
##HowTo Enable, Verify and Troubleshoot RDMA
###RDMA Drivers
`apt-get install libmlx4-1 infiniband-diags ibutils ibverbs-utils rdmacm-utils perftest`  
`apt-get install tgt`  
`apt-get install targetcli`  
`apt-get install open-iscsi-utils open-iscsi`  
###RDMA Verification
Run the following command on one server (act as a server): `ib_send_bw -d mlx4_0 -i 1 -F --report_gbits`  
Run the following command on the second server (act as a client): `ib_send_bw -d mlx4_0 -i 1 -F --report_gbits 10.22.1.1`
