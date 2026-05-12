//! ddf — DDFramework stable kernel API.
//!
//! Version: 1.0.0 (API surface, ratified at engine v1.0.0)
//! Engine:  v1.0.0 (doctrine_version this API was released against)
//!
//! This crate is the stable API surface for applications that embed
//! DDFramework. It is deliberately thin: it re-exports engine
//! primitives from [`ddf_exec_core`] and provides shim functions that
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
//! crate, not on `phantom-core` or `ghost-observer` directly. Those
//! are internal implementation and may be reorganized without
//! affecting embedders.

use std::env;
use std::path::PathBuf;
use std::process::{Command, ExitStatus};

pub use ddf_exec_core::canonical;
pub use ddf_exec_core::sha256;
pub use ddf_exec_core::timestamp;

/// Kernel API version (SemVer). Governs the stability contract of this crate.
pub const API_VERSION: &str = "1.0.0";

/// Engine doctrine_version this API was released against.
pub const ENGINE_VERSION: &str = "1.0.0";

/// Append-only hash-chained ledger operations.
#[doc(alias = "append_only_log")]
#[doc(alias = "event_log")]
pub mod ledger {
    //! Re-export of the engine ledger primitives.
    //! See `ledger/SPEC.md` for format.
    pub use ddf_exec_core::ledger::*;
}

/// Dispatch helpers for the **read-only advisor** (GHOST: mission name).
///
/// Mechanism: subprocess to `python -m ghost …` in the `ghost-observer`
/// package. Downstream Rust code may also invoke the `ddf` CLI.
#[doc(alias = "advisor")]
#[doc(alias = "advisory")]
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

    /// Run the **advisor ritual** (0006). Appends to `advisories/stream.jsonl` only.
    #[doc(alias = "run_advisor")]
    #[doc(alias = "ghost_advise")]
    pub fn advise() -> std::io::Result<ExitStatus> {
        python_cmd().args(["-m", "ghost", "advise"]).status()
    }

    /// Audit the **advisory stream** hash chain (read-only).
    #[doc(alias = "audit_advisories")]
    pub fn verify_advisories() -> std::io::Result<ExitStatus> {
        python_cmd().args(["-m", "ghost", "verify-advisories"]).status()
    }
}

/// Resolve the **engine executor** binary path (`ddf-exec`).
///
/// Resolution order:
/// 1. `DDF_EXEC_BIN` environment variable (absolute path).
/// 2. Sibling of the current executable (useful when `ddf` and
///    `ddf-exec` are co-installed).
/// 3. `ddf-exec` on `PATH`.
#[doc(alias = "ritual_executor_bin")]
#[doc(alias = "executor_path")]
#[doc(alias = "phantom_bin_path")]
pub fn exec_bin_path() -> PathBuf {
    if let Ok(p) = env::var("DDF_EXEC_BIN") {
        return PathBuf::from(p);
    }
    if let Ok(cur) = env::current_exe() {
        if let Some(parent) = cur.parent() {
            let name = if cfg!(windows) { "ddf-exec.exe" } else { "ddf-exec" };
            let candidate = parent.join(name);
            if candidate.exists() {
                return candidate;
            }
        }
    }
    PathBuf::from("ddf-exec")
}

/// Run the **verify ritual** (0001). Behavior-identical to `phantom verify`.
#[doc(alias = "verify_ledger")]
#[doc(alias = "ritual_verify")]
pub fn verify() -> std::io::Result<ExitStatus> {
    Command::new(exec_bin_path()).arg("verify").status()
}

/// Record a **doctrine amendment ritual** (0004). All arguments required.
/// `--approve` is auto-supplied; the API consumer has already decided.
#[doc(alias = "doctrine_amendment")]
pub fn amend_doctrine(
    new_version: &str,
    rationale: &str,
    domain: &str,
) -> std::io::Result<ExitStatus> {
    Command::new(exec_bin_path())
        .args([
            "amend-doctrine",
            "--version", new_version,
            "--rationale", rationale,
            "--domain", domain,
            "--approve",
        ])
        .status()
}

/// File a **waiver ritual** (0005). `--approve` is auto-supplied.
#[doc(alias = "waiver_filing")]
pub fn file_waiver(id: &str, waiver_path: &str) -> std::io::Result<ExitStatus> {
    Command::new(exec_bin_path())
        .args([
            "file-waiver",
            "--id", id,
            "--waiver", waiver_path,
            "--approve",
        ])
        .status()
}

/// **Dispatch** a registered ritual by id (zero-argument entrypoint).
/// Rituals that require arguments (`amend-doctrine`, `file-waiver`)
/// must use their dedicated functions; this covers e.g. verify (0001)
/// and advisor (0006).
#[doc(alias = "dispatch_ritual")]
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
        assert_eq!(API_VERSION, "1.0.0");
    }

    #[test]
    fn engine_version_matches_ddf_exec_core() {
        assert_eq!(ENGINE_VERSION, ddf_exec_core::DOCTRINE_VERSION);
    }

    #[test]
    fn run_ritual_rejects_args_requiring_rituals() {
        let err = run_ritual("amend-doctrine").unwrap_err();
        assert_eq!(err.kind(), std::io::ErrorKind::InvalidInput);
    }
}
