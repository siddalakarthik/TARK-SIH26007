#include "status.h"
void tark_status_init(tark_status_t*s){s->firmware_version="0.1.0";s->protocol_version=2;s->configuration_hash="UNRELEASED-PHASE1";s->output_status="DISABLED_PHASE_1";s->last_sequence=0;s->last_rejection="NOT_ENABLED";}
