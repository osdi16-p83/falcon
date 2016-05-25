Automatic Evaluation Framework is consisting of a python file named eval.py and some cfg files.

Step 0: 
Before using evaluation framework, it is assumed that the softwares are all installed properly.
In $RDMA_ROOT/apps, threre are many softwares directory, running mk file could help install relative software program. Executable files are usually configured in a directory called 'install' if using mk file to install software. 
For example: redis-server(server of database redis) is located in $RDMA_ROOT/apps/redis/install/redis-server

Step 1:
Write a cfg file for a software, in eval directory, there are already many cfg files. 
It has seven parameters: EVAL_OPTIONS, SERVER_COUNT, SERVER_PROGRAM, SERVER_INPUT, SERVER_KILL, CLIENT_PROGRAM, CLIENT_INPUT
In EVAL_OPTIONS: WITHOUT_HOOK: not use our code to hook
                 WITH_HOOK: use our code to hook
                 WITHOUT_CHECKPOINT: disable checkpoint function
                 WITH_CHECKPOINT: enable checkpoint function
                 WITHOUT_OUTPUT_COMPARE: disable output compare function
                 WITH_OUTPUT_COMPARE: enable output compare function
SERVER_COUNT: the count of servers wanted to run
SERVER_PROGRAM: the location of the server of software (for example: redis-server is located in $RDMA_ROOT/apps/redis/install/redis-server)
SERVER_INPUT: other parameters needed to pass into the program
SERVER_KILL: method to kill relative program
CLIENT_PROGRAM: the benchmark to test this software's performance
CLIENT_INPUT: other parameters needed to pass into the benchmark (for example: number of clients)

Step 2:
Run eval.py in the following method, -f means filename
> python eval.py -f redis.cfg
The process of evaluation will last for around one minute, wait patiently.
