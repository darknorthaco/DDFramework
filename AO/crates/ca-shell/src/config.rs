//! Explicit paths for the shell workspace and the engine checkout (I5: no ambient cwd for roots).

use std::path::{Path, PathBuf};

/// Operator-supplied layout: shell state vs engine installation.
#[derive(Clone, Debug)]
pub struct AoConfig {
    /// Application workspace root (contains `config/`, `ledger/`, `advisories/`).
    pub shell_root: PathBuf,
    /// Path to the DDFramework engine repository root (contains `doctrine.toml`, `phantom`, `ghost-observer`).
    pub engine_root: PathBuf,
}

impl AoConfig {
    pub fn new(shell_root: PathBuf, engine_root: PathBuf) -> Self {
        Self {
            shell_root,
            engine_root,
        }
    }

    pub fn shell_ledger_path(&self) -> PathBuf {
        self.shell_root.join("ledger").join("events.jsonl")
    }

    pub fn engine_doctrine_path(&self) -> PathBuf {
        self.engine_root.join("doctrine.toml")
    }

    pub fn engine_constellation_path(&self) -> PathBuf {
        self.engine_root.join("constellation.toml")
    }

    pub fn ceremony_token_path(&self) -> PathBuf {
        self.shell_root.join("config").join("OPERATOR_APPROVAL_TOKEN")
    }
}

/// Resolve shell root: use given path or validate current dir contains `config/shell.toml`.
pub fn default_shell_root(explicit: Option<PathBuf>) -> Result<PathBuf, String> {
    if let Some(p) = explicit {
        return Ok(p);
    }
    let cwd = std::env::current_dir().map_err(|e| e.to_string())?;
    if cwd.join("config").join("shell.toml").exists() {
        return Ok(cwd);
    }
    Err(
        "could not infer shell root: pass --shell-root or run from the AO workspace directory"
            .into(),
    )
}

pub fn read_engine_root(shell_root: &Path) -> Result<PathBuf, String> {
    let p = shell_root.join("config").join("shell.toml");
    let raw = std::fs::read_to_string(&p).map_err(|e| format!("{}: {}", p.display(), e))?;
    parse_engine_root(&raw).ok_or_else(|| {
        format!(
            "config/shell.toml must contain a line `engine_root = \"<path>\"` (read {})",
            p.display()
        )
    })
}

fn parse_engine_root(toml: &str) -> Option<PathBuf> {
    for line in toml.lines() {
        let line = line.trim();
        if line.starts_with('#') || line.is_empty() {
            continue;
        }
        if let Some(rest) = line.strip_prefix("engine_root") {
            let rest = rest.trim_start();
            if let Some(r) = rest.strip_prefix('=') {
                let val = r.trim().trim_matches('"').trim_matches('\'');
                if !val.is_empty() {
                    return Some(PathBuf::from(val));
                }
            }
        }
    }
    None
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_engine_root_line() {
        let s = r#"# comment
engine_root = "/opt/DDFramework"
"#;
        assert_eq!(
            parse_engine_root(s),
            Some(PathBuf::from("/opt/DDFramework"))
        );
    }
}
