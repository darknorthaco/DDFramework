//! Append-only shell ledger entries (same canonical field set as engine ledger per `ledger/SPEC.md`).

use std::path::Path;

use ddf::canonical::Entry;
use ddf::ledger::{self, LedgerError};
use ddf::sha256::sha256_hex_file_normalized;
use ddf::timestamp::now_rfc3339;

#[derive(Debug)]
pub enum ShellLedgerError {
    Ledger(LedgerError),
    Io(std::io::Error),
}

impl std::fmt::Display for ShellLedgerError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ShellLedgerError::Ledger(e) => write!(f, "{e}"),
            ShellLedgerError::Io(e) => write!(f, "{e}"),
        }
    }
}

impl std::error::Error for ShellLedgerError {}

impl From<LedgerError> for ShellLedgerError {
    fn from(e: LedgerError) -> Self {
        ShellLedgerError::Ledger(e)
    }
}

impl From<std::io::Error> for ShellLedgerError {
    fn from(e: std::io::Error) -> Self {
        ShellLedgerError::Io(e)
    }
}

/// Build required ledger fields plus optional flat string/bool extensions.
pub fn append_shell_event(
    ledger_path: &Path,
    engine_doctrine: &Path,
    event: &str,
    version: &str,
    change: &str,
    domain: &str,
    integrity_check: bool,
    regenerative_check: bool,
    simulation_required: bool,
    disruption_considered: bool,
    extra: &[(&str, &str)],
    extra_owned: &[(String, String)],
    extra_bool: &[(&str, bool)],
) -> Result<String, ShellLedgerError> {
    let doctrine_hex = sha256_hex_file_normalized(engine_doctrine)?;
    let doctrine_hash = format!("sha256:{doctrine_hex}");

    let prev = ledger::read_head(ledger_path)?;
    let ts = now_rfc3339();

    let mut e = Entry::new();
    e.str("timestamp", ts)
        .str("event", event)
        .str("version", version.to_string())
        .str("change", change.to_string())
        .str("domain", domain.to_string())
        .boolean("integrity_check", integrity_check)
        .boolean("regenerative_check", regenerative_check)
        .boolean("simulation_required", simulation_required)
        .boolean("disruption_considered", disruption_considered)
        .str("doctrine_hash", doctrine_hash)
        .str("prev_entry_hash", prev);

    for (k, v) in extra {
        e.str(k, v.to_string());
    }
    for (k, v) in extra_owned {
        e.str(k, v.clone());
    }
    for (k, v) in extra_bool {
        e.boolean(k, *v);
    }

    Ok(ledger::append(ledger_path, &e)?)
}
