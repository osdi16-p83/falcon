#!/usr/bin/env python
# -*- coding: utf-8 -*-
#python2.7.x

import ConfigParser
import argparse
import logging
import sys
import os


def processOptions(options):
    for option in options:
        if option.endswith('HOOK'):
            hook_option = option
        elif option.endswith('CHECKPOINT'):
            checkpoint_option = option
        elif option.endswith('COMPARE'):
            compare_option = option
        else:
            logging.critical("strange option " + option)
    return hook_option,checkpoint_option,compare_option

def enableServer(config,bench):
    server_program=config.get(bench,'SERVER_PROGRAM')
    server_input=config.get(bench,'SERVER_INPUT')




def processBench(config, bench):
    logger.debug("processing: " + bench)
    eval_options = config.get(bench,'EVAL_OPTIONS').split(',')
    hook_option,check_option,compare_option = processOptions(eval_options)
    #print eval_options
    #print hook_option + check_option + compare_option
    server_count=config.getint(bench,'SERVER_COUNT')
    server_program=config.get(bench,'SERVER_PROGRAM')
    #if len(server_program)!=0:
    if hook_option == "WITH_HOOK":
        hook_program = "env node_id=myid LD_LIBRARY_PATH=$RDMA_ROOT/RDMA/.local/lib  cfg_path=$RDMA_ROOT/RDMA/target/nodes.local.cfg LD_PRELOAD=$RDMA_ROOT/RDMA/target/interpose.so "
    elif hook_option == "WITHOUT_HOOK":
        hook_program = ""
    else:
        logger.error("No such hook option")   

    if compare_option == "WITHOUT_OUTPUT_COMPARE":
        check_output = "0"
    elif compare_option == "WITH_OUTPUT_COMPARE":
        check_output = "1"
    else:
        logger.error("No such compare option")


    repeats=config.getint(bench,'REPEATS')
    server_input=config.get(bench,'SERVER_INPUT')
    server_kill=config.get(bench,'SERVER_KILL')
    client_program=config.get(bench,'CLIENT_PROGRAM')
    client_input=config.get(bench,'CLIENT_INPUT')
    client_input_list=client_input.split("|")

    testname,port_str = bench.split(" ")
    if testname == "mysql":
        hook_program = "sudo " + hook_program

    if testname == "mongodb":
        hook_program = hook_program.replace("nodes.local.cfg","nodes.mongodb.cfg")
    port = port_str.replace("port:","")
    logging.info("port: " + port)
    testscript = open(testname,"w")
    testscript.write('#! /bin/bash\n')

    testscript.write('bash db_delete.sh\n')

    if server_count == 3:
        testscript.write('ssh ' + local_host + '  "' + server_kill + '"\n' +
        'ssh ' + remote_hostone + '  "' + server_kill + '"\n' +
        'ssh ' + remote_hosttwo + '  "' + server_kill + '"\n')
    elif server_count == 1:
        testscript.write(server_kill + '\n' )

    testscript.write('ssh ' + local_host + '  "' +'sed -i \'/127.0.0.1/{n;s/.*/        port       = '+port+';/}\' $RDMA_ROOT/RDMA/target/nodes.local.cfg  "\n' +
    'ssh ' + remote_hostone + '  "' + 'sed -i \'/127.0.0.1/{n;s/.*/        port       = '+port+';/}\' $RDMA_ROOT/RDMA/target/nodes.local.cfg  "\n' +
     'ssh ' + remote_hosttwo + '  "' + 'sed -i \'/127.0.0.1/{n;s/.*/        port       = '+port+';/}\' $RDMA_ROOT/RDMA/target/nodes.local.cfg  "\n')

    testscript.write('ssh ' + local_host + '  "' +'sed -i \'/check_output/c     check_output = '+ check_output + ';\' $RDMA_ROOT/RDMA/target/nodes.local.cfg  "\n' +
    'ssh ' + remote_hostone + '  "' +'sed -i \'/check_output/c     check_output = '+ check_output + ';\' $RDMA_ROOT/RDMA/target/nodes.local.cfg  "\n' +
    'ssh ' + remote_hosttwo + '  "' +'sed -i \'/check_output/c     check_output = '+ check_output + ';\' $RDMA_ROOT/RDMA/target/nodes.local.cfg  "\n')



    if server_count == 3:
        testscript.write('ssh -f ' + local_host + '  "' + hook_program.replace("myid",node_id_one) + server_program + ' ' + server_input +'"  \n'+ 'sleep 2 \n' +
        'ssh -f ' + remote_hostone + '  "' + hook_program.replace("myid",node_id_two) + server_program + ' ' + server_input + '" \n' + 'sleep 2 \n' +
        'ssh -f ' + remote_hosttwo + '  "' + hook_program.replace("myid",node_id_thr) + server_program + ' ' + server_input + '" \n'+ 'sleep 5 \n' )
    elif server_count == 1:
        testscript.write('ssh -f ' + local_host + '  "' + hook_program.replace("myid",node_id_one) + server_program + ' ' + server_input + '" \n' + 'sleep 5 \n')

    testscript.write('skip_client=false\n')
    testscript.write('local_pid=$(ssh ' + local_host + ' pidof ' + server_program + ' | wc -l)\n')
    testscript.write('if [ "$local_pid" == "1" ]; then\n')
    testscript.write('echo ' + testname + ' in localhost is running\n')
    testscript.write('echo -e "\\n"\n')
    testscript.write('else\n')
    testscript.write('echo ' + testname + ' in localhost is breaking down\n')
    testscript.write('echo -e "\\n"\n')
    testscript.write('skip_client=true\n')
    testscript.write('fi\n')

    testscript.write('remote1_pid=$(ssh ' + remote_hostone + ' pidof ' + server_program + ' | wc -l)\n')
    testscript.write('if [ "$remote1_pid" == "1" ]; then\n')
    testscript.write('echo ' + testname + ' in remote_hostone is running\n')
    testscript.write('echo -e "\\n"\n')
    testscript.write('else\n')
    testscript.write('echo ' + testname + ' in remote_hostone is breaking down\n')
    testscript.write('echo -e "\\n"\n')
    testscript.write('skip_client=true\n')
    testscript.write('fi\n')

    testscript.write('remote2_pid=$(ssh ' + remote_hosttwo + ' pidof ' + server_program + ' | wc -l)\n')
    testscript.write('if [ "$remote2_pid" == "1" ]; then\n')
    testscript.write('echo ' + testname + ' in remote_hosttwo is running\n')
    testscript.write('echo -e "\\n"\n')
    testscript.write('else\n')
    testscript.write('echo ' + testname + ' in remote_hosttwo is breaking down\n')
    testscript.write('echo -e "\\n"\n')
    testscript.write('skip_client=true\n')
    testscript.write('fi\n')

    if testname=="clamav" or testname=="ssdb":
        testscript.write('sleep 10\n')

    testscript.write('if [ "$skip_client" = "true" ]; then\n')
    testscript.write('echo "Skip benchmark and kill all servers and restart again"\n')
    testscript.write('else\n')
    if testname == "clamav" or testname == "mediatomb":
        for client_input_part in client_input_list:
            testscript.write(client_program + ' ' + client_input_part +'  > ' + config_file.replace(".cfg","") + '_output_$1'  '\n' + 'sleep 5 \n')
    else:
        for client_input_part in client_input_list:
            testscript.write('ssh ' + test_host + '  "' + client_program + ' ' + client_input_part +'"  > ' + config_file.replace(".cfg","") + '_result/' + config_file.replace(".cfg","") + '_output_$1' +  '\n' + 'sleep 10 \n')
    testscript.write('fi\n')
    if server_count == 3:
        testscript.write('ssh ' + local_host + '  "' + server_kill + '"\n' +
        'ssh ' + remote_hostone + '  "' + server_kill + '"\n' +
        'ssh ' + remote_hosttwo + '  "' + server_kill + '"\n' + 'sleep 30')
    elif server_count == 1:
        testscript.write('ssh ' + local_host + '  "' + server_kill + '"\n')

    testscript.close()
    os.system('chmod +x '+testname)
    os.system('mkdir ' + config_file.replace(".cfg","") + '_result')
    for repeat in range(0,repeats):
        os.system('./' + testname + " " + str(repeat))
    #os.system('rm -rf ' + testname)
    #os.system(server_program + " " + server_input)
    #os.system(client_program + " " + client_input)
    #os.system(server_kill)




def readConfigFile(config_file):
        default_values = {"EVAL_OPTIONS":"WITHOUT_HOOK,WITHOUT_CHECKPOINT,WITHOUT_OUTPUT_COMPARE",
                          "SERVER_COUNT":"1","SERVER_PROGRAM":"","SERVER_INPUT":"","SERVER_KILL":"",
                          "CLIENT_PROGRAM":"","CLIENT_INPUT":""}
	try:
		newConfig = ConfigParser.ConfigParser(default_values)
		ret = newConfig.read(config_file)
	except ConfigParser.MissingSectionHeaderError as e:
		logging.error(str(e))
	except ConfigParser.ParsingError as e:
		logging.error(str(e))
	except ConfigParser.Error as e:
		logging.critical("strange error? " + str(e))
	else:
		if ret:
			return newConfig

def getConfigFullPath(config_file):
    try:
        with open(config_file) as f:
            pass
    except IOError as e:
        logging.warning("'%s' does not exist" % config_file)
        return None
    return os.path.abspath(config_file)



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-s %(levelname)-s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='/tmp/myapp.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-s: %(levelname)-s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)

    logger = logging.getLogger()

    #see if there is an environment variable
    try:
        RDMA_ROOT = os.environ["RDMA_ROOT"]
        logger.debug('RDMA_ROOT = ' + RDMA_ROOT)
    except KeyError as e:
        logger.error("Please set the environment variable " + str(e))
        sys.exit(1)

    try:
        username = os.popen('echo $USER').readline().replace("\n","")
        local_host_ip = os.popen('cat $RDMA_ROOT/apps/env/local_host').readline().replace("\n","")
        
        local_host = username + "@" + local_host_ip
        node_id_one = "0 "
        remote_hostone_ip = os.popen('cat $RDMA_ROOT/apps/env/remote_host1').readline().replace("\n","")
        remote_hostone = username + "@" + remote_hostone_ip
        node_id_two = "1 "
        remote_hosttwo_ip = os.popen('cat $RDMA_ROOT/apps/env/remote_host2').readline().replace("\n","")
        remote_hosttwo = username + "@" + remote_hosttwo_ip
        node_id_thr = "2 "
        test_host_ip = os.popen('cat $RDMA_ROOT/apps/env/test_host').readline().replace("\n","")
        test_host = username + "@" + test_host_ip
    except KeyError as e:
        logger.error("Please set the host file " + str(e))
        sys.exit(1)

    #find the location of bash and print it
    bash_path = os.popen("which bash").readlines()
    #print bash_path
    if not bash_path:
        logging.critical("cannot find shell 'bash'")
        sys.exit(1)
    else:
        bash_path = bash_path[0]
        logging.debug("find 'bash' at " + bash_path)

    #parse args and give some help how to handle this file
    parser = argparse.ArgumentParser(description='Apps Evaluation')
    parser.add_argument('--filename','-f',nargs='*',
                        type=str,
                        default=["default.cfg"],
                        help="list of configuration files")
    args = parser.parse_args()

    if args.filename.__len__() == 0:
        logging.critical(' no configuration file specified ')
        sys.exit(1)
    elif args.filename.__len__() == 1:
        logging.debug('config file: ' + ''.join(args.filename))
    else:
        logging.debug('config files: ' + ', '.join(args.filename))

    for config_file in args.filename:
        logging.info("processing '" + config_file + "'")
        full_path = getConfigFullPath(config_file)

        local_config = readConfigFile(full_path)
        if not local_config:
            logging.warning("skip " + full_path)
            continue

        benchmarks = local_config.sections()
        for benchmark in benchmarks:
            if benchmark == "default":
                continue
            processBench(local_config, benchmark)
