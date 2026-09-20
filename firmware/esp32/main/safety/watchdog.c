#include "watchdog.h"

void tark_watchdog_init(tark_watchdog_t *watchdog, uint64_t now_ns) {
    watchdog->last_kick_ns = now_ns;
    watchdog->enabled = true;
    watchdog->state = "SOFTWARE_BOUNDARY_READY";
}

void tark_watchdog_kick(tark_watchdog_t *watchdog, uint64_t now_ns) {
    if (watchdog->enabled && now_ns >= watchdog->last_kick_ns) watchdog->last_kick_ns = now_ns;
}

bool tark_watchdog_expired(const tark_watchdog_t *watchdog, uint64_t now_ns, uint64_t timeout_ns) {
    return !watchdog->enabled || now_ns < watchdog->last_kick_ns || now_ns - watchdog->last_kick_ns > timeout_ns;
}
