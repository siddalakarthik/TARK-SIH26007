#pragma once

#include <stdbool.h>
#include <stdint.h>

/* Software watchdog boundary. ESP-IDF task-watchdog registration is deferred
 * until the flashed board and scheduler configuration are verified. */
typedef struct {
    uint64_t last_kick_ns;
    bool enabled;
    const char *state;
} tark_watchdog_t;

void tark_watchdog_init(tark_watchdog_t *watchdog, uint64_t now_ns);
void tark_watchdog_kick(tark_watchdog_t *watchdog, uint64_t now_ns);
bool tark_watchdog_expired(const tark_watchdog_t *watchdog, uint64_t now_ns, uint64_t timeout_ns);
