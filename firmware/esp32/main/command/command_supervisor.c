#include "command_supervisor.h"
#include <string.h>
static const char *reject_name(command_reject_t r){switch(r){case NACK_NONE:return "NONE";case NACK_DUPLICATE_SEQUENCE:return "DUPLICATE_SEQUENCE";case NACK_OLD_SEQUENCE:return "OLD_SEQUENCE";case NACK_OUT_OF_ORDER_SEQUENCE:return "OUT_OF_ORDER_SEQUENCE";case NACK_EXPIRED_COMMAND:return "COMMAND_EXPIRED";case NACK_HEARTBEAT_TIMEOUT:return "HEARTBEAT_TIMEOUT";case NACK_CONFIGURATION_MISMATCH:return "CONFIGURATION_MISMATCH";case NACK_NOT_ENABLED:return "NOT_ENABLED";default:return "INTERNAL_FAULT";}}
void command_supervisor_init(command_supervisor_t *s){memset(s,0,sizeof(*s));s->phase1_output_disabled=true;s->last_rejection="NOT_ENABLED";}
command_reject_t command_supervisor_accept(command_supervisor_t *s,uint32_t q,uint64_t now,uint64_t until,bool match){
    command_reject_t r=NACK_NONE;
    if(!match)r=NACK_CONFIGURATION_MISMATCH;
    else if(until<=now)r=NACK_EXPIRED_COMMAND;
    else if(s->seen&&q==s->last_sequence)r=NACK_DUPLICATE_SEQUENCE;
    else if(s->seen&&q<s->last_sequence)r=NACK_OLD_SEQUENCE; /* no wrap within a session */
    if(r!=NACK_NONE){command_supervisor_force_safe_stop(s,r);return r;}
    s->seen=true;s->active=true;s->last_sequence=q;s->heartbeat_ns=now;s->local_expiry_ns=until;s->last_rejection="NONE";return NACK_NONE;
}
bool command_supervisor_heartbeat_expired(const command_supervisor_t *s,uint64_t now,uint64_t timeout){return !s->seen||now<s->heartbeat_ns||now-s->heartbeat_ns>=timeout;}
void command_supervisor_force_safe_stop(command_supervisor_t *s,command_reject_t r){s->active=false;s->phase1_output_disabled=true;s->last_rejection=reject_name(r);}
void command_supervisor_tick(command_supervisor_t *s,uint64_t now,uint64_t timeout){
    if(!s->active)return;
    if(now<s->heartbeat_ns||now>=s->local_expiry_ns)command_supervisor_force_safe_stop(s,NACK_EXPIRED_COMMAND);
    else if(command_supervisor_heartbeat_expired(s,now,timeout))command_supervisor_force_safe_stop(s,NACK_HEARTBEAT_TIMEOUT);
}
