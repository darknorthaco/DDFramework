// Genesis roundtrip test.
//
// Rebuilds the committed genesis ledger entry from known values
// using the Rust canonical serializer + SHA-256, and verifies the
// `entry_hash` matches what was computed by ledger/_write_genesis.py
// (the Python-written source of truth). This is the interop test
// that proves Rust and Python agree on canonical form.

use ddf_exec_core::canonical::Entry;

const ZERO: &str = "sha256:0000000000000000000000000000000000000000000000000000000000000000";
const EXPECTED_ENTRY_HASH: &str =
    "sha256:cac802cf5f41756834620be8bb2b64b6d175b5a541ef4cd984067a3dcc7e098e";

const DOCTRINE_HASH: &str =
    "sha256:27e11460eaa3aafe3d4910d32fbf131179c3a4386180419e5108af36a4d742af";
const CONSTELLATION_HASH: &str =
    "sha256:400b1da3dbb9e106e10b834ba00c5ca0efea390df0c72d8db88083dc4f733fdd";

const CHANGE: &str = "Ratified Constellation Doctrine v0.1.1 as constitutional layer above Shrike architectural doctrine v0.1.0. Project doctrine_version bumped 0.1.0 -> 0.2.0 (minor: added constitutional layer; no invariants weakened). Genesis ledger entry.";

#[test]
fn genesis_entry_hash_matches_committed_value() {
    let mut e = Entry::new();
    e.str("timestamp", "2026-04-20T00:00:00Z")
        .str("event", "doctrine_amendment")
        .str("version", "0.2.0")
        .str("change", CHANGE)
        .str("domain", "complicated")
        .boolean("integrity_check", true)
        .boolean("regenerative_check", true)
        .boolean("simulation_required", false)
        .boolean("disruption_considered", true)
        .str("doctrine_hash", DOCTRINE_HASH)
        .str("constellation_hash", CONSTELLATION_HASH)
        .str("prev_entry_hash", ZERO);

    let entry_hash = e.entry_hash();
    assert_eq!(
        entry_hash, EXPECTED_ENTRY_HASH,
        "Rust canonical form disagrees with committed genesis (Python-written). \
         Check canonical.rs key sorting or string escaping."
    );
}
