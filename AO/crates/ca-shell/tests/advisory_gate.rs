//! Advisory correctness: shell does not treat GHOST output as authority for privileged acts;
//! ceremony file is the gate (see SECURITY_MODEL.md).

use ca_shell::rituals::ceremony_approves_external;

#[test]
fn ceremony_requires_exact_marker() {
    assert!(!ceremony_approves_external("OPERATOR_APPROVED=0\n"));
    assert!(!ceremony_approves_external(""));
    assert!(ceremony_approves_external("# header\nOPERATOR_APPROVED=1\n"));
}
