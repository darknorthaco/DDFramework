//! phantom-core — Shrike Phantom Core library.
//!
//! Zero dependencies. Pure Rust. Tested against NIST test vectors
//! and the committed genesis ledger entry.
//!
//! Modules:
//! - `sha256`     — FIPS 180-4 pure-Rust hash (no unsafe)
//! - `canonical`  — RFC-8785-subset JSON serializer for ledger entries
//! - `ledger`     — append-only, hash-chained ledger reader/writer
//! - `timestamp`  — stdlib-only RFC 3339 formatter for UTC now

pub mod canonical;
pub mod ledger;
pub mod sha256;
pub mod timestamp;

/// Version of the Shrike architectural doctrine this binary was
/// built against (see doctrine.toml `[meta].doctrine_version`).
pub const DOCTRINE_VERSION: &str = "0.3.0";

/// Version of the Constellation (constitutional) doctrine this
/// binary was built against (see constellation.toml `[meta].version`).
pub const CONSTELLATION_VERSION: &str = "0.1.1";

/// SHA-256 of `doctrine.toml` at compile time, as `sha256:<hex>`.
/// Set by build.rs from `cargo:rustc-env`.
pub const DOCTRINE_HASH_EMBEDDED: &str = env!("SHRIKE_DOCTRINE_HASH");

/// SHA-256 of `constellation.toml` at compile time.
pub const CONSTELLATION_HASH_EMBEDDED: &str = env!("SHRIKE_CONSTELLATION_HASH");
