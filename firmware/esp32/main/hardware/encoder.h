#pragma once

#include <stdbool.h>
#include <stdint.h>

/* Software-only encoder boundary.  It reports wheel response, never ground
 * speed.  GPIO capture is deliberately deferred until supply/interface are
 * verified against the purchased JGB37-520 encoder documentation. */
typedef struct {
    int32_t left_pulses;
    int32_t right_pulses;
    uint64_t timestamp_ns;
    bool connected;
    const char *state;
} encoder_state_t;

void encoder_init(encoder_state_t *encoder);
void encoder_record_simulated_counts(encoder_state_t *encoder, int32_t left, int32_t right, uint64_t timestamp_ns);
bool encoder_has_fresh_signal(const encoder_state_t *encoder, uint64_t now_ns, uint64_t timeout_ns);
