#pragma once

#include <stdbool.h>

/*
 * Phase-2 software boundary for the Cytron MDD10A.  The physical mapping is
 * retained in the implementation notes, but this firmware has no GPIO/PWM
 * binding until the actual board, MDD10A variant and wiring are verified.
 */
typedef struct {
    float requested_left;
    float requested_right;
    float applied_left;
    float applied_right;
    bool phase1_output_disabled;
    const char *state;
} motor_driver_t;

void motor_driver_init(motor_driver_t *driver);
bool motor_driver_apply_bounded(motor_driver_t *driver, float left, float right);
void motor_driver_safe_stop(motor_driver_t *driver);
