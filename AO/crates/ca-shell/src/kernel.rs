//! Kernel boundary integration: verify + advisor subprocesses only (`ddf`).

use std::path::Path;
use std::process::Command;

/// Run engine `verify` ritual from `engine_root` (sets cwd so `phantom` finds doctrine).
pub fn engine_verify(engine_root: &Path) -> std::io::Result<std::process::ExitStatus> {
    let bin = ddf::phantom_bin_path();
    Command::new(bin)
        .current_dir(engine_root)
        .arg("verify")
        .status()
}

/// Run advisor over the **engine** ledger in `engine_root` (GHOST reads engine paths).
pub fn engine_advise(engine_root: &Path) -> std::io::Result<std::process::ExitStatus> {
    let python = std::env::var("DDF_PYTHON").unwrap_or_else(|_| "python".to_string());
    let ghost_dir = engine_root.join("ghost-observer");
    Command::new(python)
        .current_dir(engine_root)
        .env("PYTHONPATH", ghost_dir)
        .args(["-m", "ghost", "advise"])
        .status()
}
