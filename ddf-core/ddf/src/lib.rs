//! ddf — DDFramework stable kernel API.
//!
//! Version: 0.1.0 (API surface)
//! Engine:  v0.7.0 (doctrine_version this API was released against)
//!
//! This crate is the stable API surface for applications that embed
//! DDFramework. It is deliberately thin: it re-exports engine
//! primitives from [`phantom_core`] and provides shim functions that
//! delegate to the `phantom` binary for CLI rituals. There is no new
//! behavior here; `ddf verify` is byte-exact with `phantom verify` by
//! construction (it invokes the same binary).
//!
//! ## Stability contract
//!
//! - This crate's public API is governed by the kernel API version
//!   (see [`API_VERSION`]).
//! - The engine doctrine version ([`ENGINE_VERSION`]) may evolve
//!   independently; the kernel API promises to remain source- and
//!   behavior-compatible across engine patch and minor bumps.
//! - Weakening the API surface is a major bump.
//!
//! ## Embeddability
//!
//! Downstream applications (Application Era, v5.0.0+) depend on this
//! crate, not on `phantom-core`, `hyperion-net`, or `ghost-observer`
//! directly. Those are internal implementation and may be reorganized
//! without affecting embedders.

use std::env;
use std::path::PathBuf;
use std::process::{Command, ExitStatus};

pub use phantom_core::canonical;
pub use phantom_core::sha256;
pub use phantom_core::timestamp;

/// Kernel API version (SemVer). Governs the stability contract of this crate.
pub const API_VERSION: &str = "0.1.0";

/// Engine doctrine_version this API was released against.
pub const ENGINE_VERSION: &str = "0.7.0";

/// Append-only hash-chained ledger operations.
pub mod ledger {
    //! Re-export of the engine ledger primitives.
    //! See `ledger/SPEC.md` for format.
    pub use phantom_core::ledger::*;
}

/// Dispatch helpers for the GHOST advisory engine.
///
/// GHOST lives in the `ghost-observer` Python package. These
/// functions shell out to `python -m ghost ...`. Downstream Rust
/// applications can also call the `ddf` CLI directly or spawn their
/// own Python process.
pub mod ghost {
    use std::env;
    use std::process::{Command, ExitStatus};

    fn python_cmd() -> Command {
        let python = env::var("DDF_PYTHON").unwrap_or_else(|_| "python".to_string());
        let mut cmd = Command::new(python);
        // Make the ghost-observer package importable from the workspace.
        if env::var_os("PYTHONPATH").is_none() {
            cmd.env("PYTHONPATH", "ghost-observer");
        }
        cmd
    }

    /// Run the GHOST advisor (ritual 0006). Writes to `advisories/stream.jsonl`.
    pub fn advise() -> std::io::Result<ExitStatus> {
        python_cmd().args(["-m", "ghost", "advise"]).status()
    }

    /// Audit the advisory stream hash chain.
    pub fn verify_advisories() -> std::io::Result<ExitStatus> {
        python_cmd().args(["-m", "ghost", "verify-advisories"]).status()
    }
}

/// Resolve the `phantom` binary path.
///
/// Resolution order:
/// 1. `DDF_PHANTOM_BIN` environment variable (absolute path).
/// 2. Sibling of the current executable (useful when `ddf` and
///    `phantom` are co-installed).
/// 3. `phantom` on `PATH`.
pub fn phantom_bin_path() -> PathBuf {
    if let Ok(p) = env::var("DDF_PHANTOM_BIN") {
        return PathBuf::from(p);
    }
    if let Ok(cur) = env::current_exe() {
        if let Some(parent) = cur.parent() {
            let name = if cfg!(windows) { "phantom.exe" } else { "phantom" };
            let candidate = parent.join(name);
            if candidate.exists() {
                return candidate;
            }
        }
    }
    PathBuf::from("phantom")
}

/// Run the verify ritual (0001). Behavior-identical to `phantom verify`.
pub fn verify() -> std::io::Result<ExitStatus> {
    Command::new(phantom_bin_path()).arg("verify").status()
}

/// Record a doctrine amendment (0004). All arguments required.
/// `--approve` is auto-supplied; the API consumer has already decided.
pub fn amend_doctrine(
    new_version: &str,
    rationale: &str,
    domain: &str,
) -> std::io::Result<ExitStatus> {
    Command::new(phantom_bin_path())
        .args([
            "amend-doctrine",
            "--version", new_version,
            "--rationale", rationale,
            "--domain", domain,
            "--approve",
        ])
        .status()
}

/// File a waiver (0005). `--approve` is auto-supplied.
pub fn file_waiver(id: &str, waiver_path: &str) -> std::io::Result<ExitStatus> {
    Command::new(phantom_bin_path())
        .args([
            "file-waiver",
            "--id", id,
            "--waiver", waiver_path,
            "--approve",
        ])
        .status()
}

/// Dispatch a registered ritual by id. Rituals that require arguments
/// (amend-doctrine, file-waiver) must be invoked through their
/// dedicated API functions; `run_ritual` is the zero-argument entry
/// point for rituals like verify and ghost-advise.
pub fn run_ritual(id: &str) -> std::io::Result<ExitStatus> {
    match id {
        "0001" | "verify" => verify(),
        "0006" | "ghost-advise" => ghost::advise(),
        other => Err(std::io::Error::new(
            std::io::ErrorKind::InvalidInput,
            format!(
                "ritual '{}' requires explicit arguments; use the dedicated API function",
                other
            ),
        )),
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn api_version_is_reported() {
        assert_eq!(API_VERSION, "0.1.0");
    }

    #[test]
    fn engine_version_matches_phantom_core() {
        assert_eq!(ENGINE_VERSION, phantom_core::DOCTRINE_VERSION);
    }

    #[test]
    fn run_ritual_rejects_args_requiring_rituals() {
        let err = run_ritual("amend-doctrine").unwrap_err();
        assert_eq!(err.kind(), std::io::ErrorKind::InvalidInput);
    }
}
