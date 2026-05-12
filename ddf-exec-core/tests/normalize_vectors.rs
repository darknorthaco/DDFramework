// Line-ending normalization tests.
//
// Proves `strip_cr` + `sha256_hex` produces the same digest for
// CRLF and LF versions of the same logical content. This is what
// makes `doctrine_hash` values platform-independent.

use ddf_exec_core::sha256::{sha256_hex, strip_cr};

#[test]
fn strip_cr_removes_all_carriage_returns() {
    assert_eq!(strip_cr(b"a\r\nb\r\nc"), b"a\nb\nc");
    assert_eq!(strip_cr(b"\r\r\r"), b"");
    assert_eq!(strip_cr(b"no-crs-here"), b"no-crs-here");
}

#[test]
fn crlf_and_lf_hash_identically_after_normalize() {
    let crlf = b"hello\r\nworld\r\n";
    let lf = b"hello\nworld\n";
    let h_crlf = sha256_hex(&strip_cr(crlf));
    let h_lf = sha256_hex(&strip_cr(lf));
    assert_eq!(h_crlf, h_lf);
    // Sanity: without normalization, they differ.
    assert_ne!(sha256_hex(crlf), sha256_hex(lf));
}

#[test]
fn empty_input_unchanged() {
    assert_eq!(strip_cr(b""), b"");
}
