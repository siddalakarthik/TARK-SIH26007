#include "encoder.h"

void encoder_init(encoder_state_t *encoder) {
    encoder->left_pulses = 0;
    encoder->right_pulses = 0;
    encoder->timestamp_ns = 0;
    encoder->connected = false;
    encoder->state = "NOT_CONNECTED_PHASE_2";
}

void encoder_record_simulated_counts(encoder_state_t *encoder, int32_t left, int32_t right, uint64_t timestamp_ns) {
    encoder->left_pulses = left;
    encoder->right_pulses = right;
    encoder->timestamp_ns = timestamp_ns;
    encoder->connected = true;
    encoder->state = "SIMULATION_WHEEL_RESPONSE";
}

bool encoder_has_fresh_signal(const encoder_state_t *encoder, uint64_t now_ns, uint64_t timeout_ns) {
    return encoder->connected && now_ns >= encoder->timestamp_ns && now_ns - encoder->timestamp_ns <= timeout_ns;
}
