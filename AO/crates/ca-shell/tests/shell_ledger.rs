//! Shell ledger append + hash chain (replay) using the engine's ledger primitives via `ddf`.

use std::path::PathBuf;

use ca_shell::config::AoConfig;
use ca_shell::rituals::{self, ActEffectClass};
use ddf::ledger;

fn workspace_engine_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../..")
}

fn temp_shell_with_config(engine_root: &std::path::Path) -> PathBuf {
    let mut dir = std::env::temp_dir();
    dir.push(format!(
        "ao_shell_test_{}_{}",
        std::process::id(),
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_nanos())
            .unwrap_or(0)
    ));
    let _ = std::fs::remove_dir_all(&dir);
    std::fs::create_dir_all(dir.join("config")).expect("mkdir config");
    std::fs::create_dir_all(dir.join("ledger")).expect("mkdir ledger");
    std::fs::write(
        dir.join("config/shell.toml"),
        format!(
            r#"# test
engine_root = "{}"
"#,
            engine_root.display()
        ),
    )
    .expect("write shell.toml");
    dir
}

#[test]
fn propose_then_verify_chain() {
    let engine = workspace_engine_root();
    let tmp = temp_shell_with_config(&engine);
    let cfg = AoConfig::new(tmp.clone(), engine);

    let h1 = rituals::ritual_propose(&cfg, "p1", "first", "complicated").expect("propose");
    assert!(h1.starts_with("sha256:"));
    let h2 = rituals::ritual_propose(&cfg, "p2", "second", "complicated").expect("propose2");
    assert_ne!(h1, h2);

    let path = cfg.shell_ledger_path();
    let (n, head) = ledger::verify_chain(&path).expect("chain");
    assert_eq!(n, 2);
    assert_eq!(head, h2);
    let _ = std::fs::remove_dir_all(&tmp);
}

#[test]
fn act_external_requires_ceremony() {
    let engine = workspace_engine_root();
    let tmp = temp_shell_with_config(&engine);
    let cfg = AoConfig::new(tmp.clone(), engine);

    rituals::ritual_propose(&cfg, "p1", "x", "complicated").expect("propose");

    let err = rituals::ritual_act(
        &cfg,
        "p1",
        "danger-tool",
        ActEffectClass::External,
        None,
        "complicated",
    )
    .expect_err("should require ceremony");
    assert!(err.to_string().contains("ceremony"));
    let _ = std::fs::remove_dir_all(&tmp);
}
