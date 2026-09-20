#include "motor_driver.h"

static float clamp_unit(float value) {
    if (value > 1.0f) return 1.0f;
    if (value < -1.0f) return -1.0f;
    return value;
}

void motor_driver_init(motor_driver_t *driver) {
    driver->requested_left = 0.0f;
    driver->requested_right = 0.0f;
    driver->applied_left = 0.0f;
    driver->applied_right = 0.0f;
    driver->phase1_output_disabled = true;
    driver->state = "DISABLED_PHASE_1";
}

bool motor_driver_apply_bounded(motor_driver_t *driver, float left, float right) {
    driver->requested_left = clamp_unit(left);
    driver->requested_right = clamp_unit(right);
    /* The only permitted Phase-1 result is an electrical-output-safe zero. */
    driver->applied_left = 0.0f;
    driver->applied_right = 0.0f;
    driver->state = "DISABLED_PHASE_1";
    return false;
}

void motor_driver_safe_stop(motor_driver_t *driver) {
    driver->requested_left = 0.0f;
    driver->requested_right = 0.0f;
    driver->applied_left = 0.0f;
    driver->applied_right = 0.0f;
    driver->state = "DISABLED_PHASE_1";
}
