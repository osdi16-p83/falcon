# Falcon
This project combines RDMA and Paxos.
The initial result can be found [here](https://docs.google.com/spreadsheets/d/1XFwAh-SRHdBxu_PfRj2TiUBRuhfW-YC_pPDOC-TFdho/edit?usp=sharing).  
After May 10th, we did more **scalability testing** and you may check it  [here](https://docs.google.com/spreadsheets/d/1rHpv_gA_SS8XpS4sq5aLFjr_ztEPhTUH-r-1fR1_u60/edit?usp=sharing).
  
OS: Ubuntu 14.04.02 64bit.
## How to run
### Install the dependencies for the program
Use $RDMA_ROOT/RDMA/mk to download and install the dependencies for the program.
### Install the applications
We have prepared all the Makefiles for you in each application's directory.
### Run the evaluation framework
For example, to run Redis hooked by Falcon, just go to $RDMA_ROOT/eval and run `python eval.py -f redis-output.cfg`. After that, you can collect the results by `cd current`.
