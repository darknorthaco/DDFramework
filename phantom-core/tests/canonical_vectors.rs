// Canonical-form serialization tests.
//
// Verifies:
// 1. Keys are sorted byte-wise.
// 2. No whitespace.
// 3. Strings and bools serialize correctly.
// 4. Round-trip against hand-computed expected bytes.

use phantom_core::canonical::Entry;
use phantom_core::sha256::sha256_hex;

#[test]
fn empty_entry() {
    let e = Entry::new();
    assert_eq!(e.canonical_bytes(), b"{}");
}

#[test]
fn single_string_field() {
    let mut e = Entry::new();
    e.str("event", "verify.result");
    assert_eq!(e.canonical_bytes(), br#"{"event":"verify.result"}"#);
}

#[test]
fn keys_are_sorted() {
    let mut e = Entry::new();
    e.str("z", "1").str("a", "2").str("m", "3");
    assert_eq!(e.canonical_bytes(), br#"{"a":"2","m":"3","z":"1"}"#);
}

#[test]
fn booleans_literal() {
    let mut e = Entry::new();
    e.boolean("ok", true).boolean("bad", false);
    assert_eq!(e.canonical_bytes(), br#"{"bad":false,"ok":true}"#);
}

#[test]
fn string_escapes() {
    let mut e = Entry::new();
    e.str("s", "a\"b\\c\nd");
    assert_eq!(e.canonical_bytes(), br#"{"s":"a\"b\\c\nd"}"#);
}

#[test]
fn entry_hash_deterministic() {
    let mut e = Entry::new();
    e.str("event", "test").boolean("ok", true);
    let h1 = e.entry_hash();
    let h2 = e.entry_hash();
    assert_eq!(h1, h2);
    // Verify the hash matches a hand computation:
    let expected_canonical = br#"{"event":"test","ok":true}"#;
    let expected = format!("sha256:{}", sha256_hex(expected_canonical));
    assert_eq!(h1, expected);
}
