//! hyperion-net — Shrike Hyperion Fabric (skeleton).
//!
//! The Hyperion layer is the network fabric that gives a collection
//! of Phantom nodes the feel of co-location: predictive prewarming,
//! routing, continuity across disconnection. In Phase 2 this crate
//! only declares its module shape; no transport code exists yet.
//!
//! Doctrinal anchors:
//! - Constellation §3 (conceptual integrity): each module here has
//!   one purpose.
//! - DOCTRINE §II.3 (Hyperion): every action is a transport for a
//!   Phantom ritual or a cache-warming hint requested by Phantom.
//!   This crate does NOT perform rituals of its own.

/// Node-to-node routing decisions. Placeholder.
pub mod routing {
    //! Hyperion routing — empty in Phase 2.
    //! Will accept signed Phantom ritual envelopes and choose a path.
}

/// Wire-level transports. Placeholder.
/// Phase 3 will add a TCP transport; eventually the C-primitives
/// layer under `c-primitives/` supplies raw-socket primitives for
/// platforms where Rust's stdlib is insufficient.
pub mod transport {
    //! Hyperion transports — empty in Phase 2.
}

/// Continuity across disconnection (farcaster-like resume).
/// Placeholder.
pub mod continuity {
    //! Hyperion continuity — empty in Phase 2.
}

/// Returns the crate version, provided so downstream code can log it.
pub fn version() -> &'static str {
    env!("CARGO_PKG_VERSION")
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn crate_version_is_reported() {
        assert_eq!(version(), "0.3.0");
    }
}
