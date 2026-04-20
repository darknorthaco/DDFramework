// Ledger append + verify_chain roundtrip test.
//
// Writes several entries into a temp file, then verifies the chain
// validates end to end.

use phantom_core::canonical::Entry;
use phantom_core::ledger::{self, ZERO_HASH};
use std::path::PathBuf;

fn temp_ledger(name: &str) -> PathBuf {
    let mut p = std::env::temp_dir();
    p.push(format!("shrike_test_ledger_{}_{}.jsonl", name, std::process::id()));
    let _ = std::fs::remove_file(&p);
    p
}

#[test]
fn empty_ledger_head_is_zero() {
    let path = temp_ledger("empty");
    let head = ledger::read_head(&path).expect("empty read");
    assert_eq!(head, ZERO_HASH);
}

#[test]
fn append_and_chain_three_entries() {
    let path = temp_ledger("three");
    let _ = std::fs::remove_file(&path);

    for i in 0..3 {
        let prev = ledger::read_head(&path).expect("head");
        let mut e = Entry::new();
        e.str("timestamp", "2026-04-20T00:00:00Z")
            .str("event", "test.append")
            .str("version", "0.3.0")
            .str("change", format!("entry {}", i))
            .str("domain", "complicated")
            .boolean("integrity_check", true)
            .boolean("regenerative_check", true)
            .boolean("simulation_required", false)
            .boolean("disruption_considered", false)
            .str("doctrine_hash", "sha256:deadbeef")
            .str("constellation_hash", "sha256:cafef00d")
            .str("prev_entry_hash", prev);
        let _new_head = ledger::append(&path, &e).expect("append");
    }

    let (count, _head) = ledger::verify_chain(&path).expect("chain valid");
    assert_eq!(count, 3);

    let _ = std::fs::remove_file(&path);
}
