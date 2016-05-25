#include "../include/ev_mgr/check_point_thread.h"
#include "../include/util/debug.h"
#include "../include/ev_mgr/ev_mgr.h"
// Unix socket echo server

#include <event2/listener.h>
#include <event2/bufferevent.h>
#include <event2/buffer.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <pthread.h>
#include <sys/stat.h> 
#include <fcntl.h>

#define UNIX_SOCK_PATH "/tmp/checkpoint.server.sock"
#define UNIX_CMD_disconnect "disconnect"
#define UNIX_CMD_reconnect "reconnect"

void accept_error_cb(struct evconnlistener *listener, void *ctx){
        struct event_base *base = evconnlistener_get_base(listener);
        int err = EVUTIL_SOCKET_ERROR();
        debug_log("[check point] Got an error %d (%s) on the listener.\n", err, evutil_socket_error_to_string(err));
        event_base_loopexit(base, NULL);
}

void* call_disconnect_start(void *argv){
	debug_log("[check point] disconnct_inner() is called at a new thread: %lu\n",(unsigned long)pthread_self());
	int ret = disconnct_inner();
	debug_log("[check point] disconnct_inner() is finished and returned(%d) %lu\n",ret, (unsigned long)pthread_self());
	return NULL;
}
void* call_reconnect_start(void * argv){
    debug_log("[check point] reconnect_inner_set_flag() is called at a new thread: %lu\n",(unsigned long)pthread_self());
    int ret = reconnect_inner_set_flag();
    debug_log("[check point] reconnect_inner_set_flag() is finished and returned(%d) %lu\n",ret, (unsigned long)pthread_self());
    return NULL;
}
#define RE_DBG_MSG "reconnect is called.\n\n"
void unix_read_cb(struct bufferevent *bev, void *ctx){
        struct evbuffer *input = bufferevent_get_input(bev);
        struct evbuffer *output = bufferevent_get_output(bev);
        size_t len = evbuffer_get_length(input);
        char *data;
        data = malloc(len);
        evbuffer_copyout(input, data, len);
        debug_log("[check point] read data:#%s#\n",data);

        int dbg_fd = open("/tmp/re.dbg.log",O_RDWR|O_CREAT|O_SYNC|O_TRUNC,0777);
        if (-1 != dbg_fd){
            write(dbg_fd,data,len);
            char buff[512];
            sprintf(buff,"\npid: %d, thread id:%lu\n",getpid(),(unsigned long)pthread_self());
            write(dbg_fd,buff,strlen(buff));
        }
        int dis_cmp = strncmp(data,UNIX_CMD_disconnect,strlen(UNIX_CMD_disconnect));
        int re_cmp = strncmp(data,UNIX_CMD_reconnect,strlen(UNIX_CMD_reconnect));
        int ret=0;
        if (0==dis_cmp){ // got a command
            debug_log("[check point] I will call disconnct_inner(). In a new thread to avoid deadloop\n");
            pthread_t thread_id;
            ret=pthread_create(&thread_id,NULL,&call_disconnect_start,NULL);
    		if (ret){ // On success, pthread_create() returns 0
    			debug_log("[check point] call disconnct_inner() in a new thread failed. err:%d\n", ret);	
    		}
        }
        if (0==re_cmp){// try other commands
            debug_log("[check point] I will call reconnect_inner() in a new thread.\n");
            pthread_t thread_id;
            ret=pthread_create(&thread_id,NULL,&call_reconnect_start,NULL);
            if (ret){ 
                debug_log("[check point] call reconnect_inner_set_flag() in a new thread failed. err:%d\n", ret);    
                if (-1!=dbg_fd){
                    char* dbg_msg="\reconnect_inner_set_flag error\n";
                    write(dbg_fd,dbg_msg,strlen(dbg_msg));
                }               
            }else{// On success, pthread_create() returns 0
                if (-1!=dbg_fd){
                    char* dbg_msg="\reconnect_inner_set_flag ok\n";
                    write(dbg_fd,dbg_msg,strlen(dbg_msg));
                }
            }
        }
        if (-1!=dbg_fd){
            close(dbg_fd);
        }
        if (0==ret){
                evbuffer_add_printf(output,"OK\n");
        }else{
                evbuffer_add_printf(output,"ERR\n");
        }
}

void unix_event_cb(struct bufferevent *bev, short events, void *ctx){
        if (events & BEV_EVENT_ERROR){
                debug_log("[check point] Error from bufferevent.\n");
        }
        if (events & (BEV_EVENT_EOF | BEV_EVENT_ERROR)) {
                debug_log("[check point] client has quited.\n");
                bufferevent_free(bev);
        }
}

// When a unix socket accepts a new client, it will register two functions read and event.
void accept_conn_cb(struct evconnlistener *listener, evutil_socket_t fd, struct sockaddr *address, int socklen, void *ctx){
        debug_log("[check point] on accepted.\n");
        struct event_base *base = evconnlistener_get_base(listener);
        // socket will be closed on free
        struct bufferevent *bev = bufferevent_socket_new(base, fd, BEV_OPT_CLOSE_ON_FREE);
        // register two callback functions read and event
        bufferevent_setcb(bev, unix_read_cb, NULL, unix_event_cb, NULL);
        bufferevent_enable(bev, EV_READ | EV_WRITE);
}


int start_unix_server_loop(){
        struct event_base *base;
        struct evconnlistener *listener;
        struct sockaddr_un sin;
        base = event_base_new();
        if (!base) {
                debug_log("[check point] Couldn't open event base unix socket.\n");
                return -1;
        }
        memset(&sin, 0, sizeof(sin));
        sin.sun_family = AF_UNIX;
        strcpy(sin.sun_path, UNIX_SOCK_PATH);
        // remove socket first
        unlink(UNIX_SOCK_PATH);
        listener = evconnlistener_new_bind(base, accept_conn_cb, NULL,
                               LEV_OPT_CLOSE_ON_FREE | LEV_OPT_REUSEABLE, -1,
                               (struct sockaddr *) &sin, sizeof(sin));
        if (!listener){
                debug_log("[check point] Couldn't create unix listener.\n");
                return -2;
        }
        evconnlistener_set_error_cb(listener, accept_error_cb);
       	debug_log("[check point] Unix socket will be ready to accept at %s\n",UNIX_SOCK_PATH);
        event_base_dispatch(base); // It will loop
	    event_base_free(base);
        return 0;
}

void* check_point_thread_start(void* argv){
	debug_log("[check_point] thread started. cmd:%s and cmd:%s\n",UNIX_CMD_disconnect,UNIX_CMD_reconnect);
	start_unix_server_loop();
	return NULL;
}
