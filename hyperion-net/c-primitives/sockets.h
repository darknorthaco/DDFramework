/*
 * Shrike — hyperion-net c-primitives: sockets.h
 *
 * Phase 2 status: SHAPE ONLY. No implementation is linked from Rust.
 * These declarations reserve the FFI surface for future phases
 * (likely Phase 5 when transports go live).
 *
 * 100-year rationale (LANGUAGES.md §3.1): the C layer exists so the
 * ABI between Rust and the operating system remains stable even
 * if the Rust crate evolves. C ABI is the longest-lived binary
 * contract we have access to.
 *
 * Target: ISO C11. No GNU extensions.
 */

#ifndef SHRIKE_HYPERION_SOCKETS_H
#define SHRIKE_HYPERION_SOCKETS_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque handle for a platform socket. */
typedef struct shrike_sock shrike_sock;

/* Return codes. 0 = OK; negative = error. */
enum shrike_sock_status {
    SHRIKE_SOCK_OK            =  0,
    SHRIKE_SOCK_ERR_UNSUPPORTED = -1,
    SHRIKE_SOCK_ERR_IO          = -2,
    SHRIKE_SOCK_ERR_TIMEOUT     = -3
};

/*
 * Phase 2 declarations — NOT YET IMPLEMENTED.
 *
 * shrike_sock_open():  Reserve a socket for Hyperion traffic.
 * shrike_sock_close(): Release a socket.
 *
 * Signatures are stable contracts for the future implementation.
 */
int32_t shrike_sock_open(shrike_sock **out, const char *addr, uint16_t port);
int32_t shrike_sock_close(shrike_sock *s);

#ifdef __cplusplus
}
#endif

#endif /* SHRIKE_HYPERION_SOCKETS_H */
