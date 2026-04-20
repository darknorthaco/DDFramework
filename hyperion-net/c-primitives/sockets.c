/*
 * Shrike — hyperion-net c-primitives: sockets.c
 *
 * Phase 2 status: STUB. Declarations present; bodies return
 * SHRIKE_SOCK_ERR_UNSUPPORTED. This file is intentionally not
 * compiled or linked from Rust in Phase 2 — it exists to reserve
 * the ABI and to be reviewable as design intent.
 *
 * Target: ISO C11. Compile-clean with:
 *   cc -std=c11 -Wall -Wextra -Wpedantic -c sockets.c
 */

#include "sockets.h"

int32_t shrike_sock_open(shrike_sock **out, const char *addr, uint16_t port) {
    (void)out;
    (void)addr;
    (void)port;
    return SHRIKE_SOCK_ERR_UNSUPPORTED;
}

int32_t shrike_sock_close(shrike_sock *s) {
    (void)s;
    return SHRIKE_SOCK_ERR_UNSUPPORTED;
}
