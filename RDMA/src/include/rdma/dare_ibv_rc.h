#ifndef DARE_IBV_RC_H
#define DARE_IBV_RC_H

#include <infiniband/verbs.h> /* OFED stuff */
#include "dare_ibv.h"

#define Q_DEPTH 8192
#define S_DEPTH 4096
#define S_DEPTH_ 4095

struct cm_con_data_t {
	rem_mem_t log_mr;
	uint32_t type;
	uint32_t idx;
	uint16_t lid;
	uint8_t gid[16];
	uint32_t qpns;
}__attribute__ ((packed));

typedef enum communication_type_t{
    JOIN=1,
    DESTROY=2,
}communication_type;

int rc_init();
void rc_free();

int post_send( uint32_t server_id, void *buf, uint32_t len, struct ibv_mr *mr, enum ibv_wr_opcode opcode, rem_mem_t *rm, int send_flags, int poll_completion);
int rc_disconnect_server();

#endif /* DARE_IBV_RC_H */
