//! Application ritual kinds: each maps to one append-only shell ledger line.
//!
//! Contracts are documented in `RITUALS.md` at the application repo root.

use std::fs;
use std::path::Path;

use crate::config::AoConfig;
use crate::kernel;
use crate::ledger_record::{append_shell_event, ShellLedgerError};

const APP_VERSION: &str = "0.1.0";

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum RitualKind {
    Propose,
    Evaluate,
    Act,
    Reflect,
    Simulate,
}

impl RitualKind {
    pub fn event_name(self) -> &'static str {
        match self {
            RitualKind::Propose => "agent.propose",
            RitualKind::Evaluate => "agent.evaluate",
            RitualKind::Act => "agent.act",
            RitualKind::Reflect => "agent.reflect",
            RitualKind::Simulate => "agent.simulate",
        }
    }
}

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum ActEffectClass {
    LedgerOnly,
    External,
}

#[derive(Debug)]
pub enum RitualError {
    Shell(ShellLedgerError),
    EngineVerifyFailed(String),
    CeremonyRequired,
    CeremonyInvalid(String),
}

impl std::fmt::Display for RitualError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RitualError::Shell(e) => write!(f, "{e}"),
            RitualError::EngineVerifyFailed(s) => write!(f, "engine verify failed: {s}"),
            RitualError::CeremonyRequired => {
                write!(f, "privileged act requires --ceremony path with OPERATOR_APPROVED=1")
            }
            RitualError::CeremonyInvalid(s) => write!(f, "ceremony file invalid: {s}"),
        }
    }
}

impl std::error::Error for RitualError {}

impl From<ShellLedgerError> for RitualError {
    fn from(e: ShellLedgerError) -> Self {
        RitualError::Shell(e)
    }
}

fn require_engine_ok(cfg: &AoConfig) -> Result<(), RitualError> {
    let st = kernel::engine_verify(&cfg.engine_root).map_err(|e| {
        RitualError::EngineVerifyFailed(format!("could not spawn phantom verify: {e}"))
    })?;
    if st.success() {
        Ok(())
    } else {
        Err(RitualError::EngineVerifyFailed(format!("status {st}")))
    }
}

fn read_ceremony(path: &Path) -> Result<String, RitualError> {
    fs::read_to_string(path)
        .map_err(|e| RitualError::CeremonyInvalid(format!("read {}: {e}", path.display())))
}

/// Returns true if `content` contains a line exactly `OPERATOR_APPROVED=1` (after trim).
pub fn ceremony_approves_external(content: &str) -> bool {
    for line in content.lines() {
        let t = line.trim();
        if t == "OPERATOR_APPROVED=1" {
            return true;
        }
    }
    false
}

/// `agent.propose` — record intent; no engine verify gate (read-only on engine).
pub fn ritual_propose(
    cfg: &AoConfig,
    proposal_id: &str,
    summary: &str,
    domain: &str,
) -> Result<String, RitualError> {
    let ledger = cfg.shell_ledger_path();
    let doctrine = cfg.engine_doctrine_path();
    append_shell_event(
        &ledger,
        &doctrine,
        RitualKind::Propose.event_name(),
        APP_VERSION,
        summary,
        domain,
        true,
        true,
        false,
        true,
        &[
            ("proposal_id", proposal_id),
            ("ritual_id", "ao-0001"),
            ("schema", "1"),
        ],
        &[],
        &[],
    )
    .map_err(RitualError::from)
}

/// `agent.evaluate` — record evaluation; requires engine verify (safety envelope).
pub fn ritual_evaluate(
    cfg: &AoConfig,
    proposal_id: &str,
    verdict: &str,
    domain: &str,
) -> Result<String, RitualError> {
    require_engine_ok(cfg)?;
    let ledger = cfg.shell_ledger_path();
    let doctrine = cfg.engine_doctrine_path();
    append_shell_event(
        &ledger,
        &doctrine,
        RitualKind::Evaluate.event_name(),
        APP_VERSION,
        "agent evaluation recorded",
        domain,
        true,
        true,
        false,
        true,
        &[
            ("proposal_id", proposal_id),
            ("verdict", verdict),
            ("ritual_id", "ao-0002"),
            ("schema", "1"),
        ],
        &[],
        &[],
    )
    .map_err(RitualError::from)
}

/// `agent.act` — record act; external class requires operator ceremony file.
pub fn ritual_act(
    cfg: &AoConfig,
    proposal_id: &str,
    tool_id: &str,
    effect: ActEffectClass,
    ceremony_path: Option<&Path>,
    domain: &str,
) -> Result<String, RitualError> {
    let external = matches!(effect, ActEffectClass::External);
    if external {
        let path = ceremony_path.ok_or(RitualError::CeremonyRequired)?;
        let content = read_ceremony(path)?;
        if !ceremony_approves_external(&content) {
            return Err(RitualError::CeremonyRequired);
        }
    }

    require_engine_ok(cfg)?;

    let ledger = cfg.shell_ledger_path();
    let doctrine = cfg.engine_doctrine_path();
    let ceremony_hash: Option<String> = ceremony_path
        .map(|p| {
            let bytes = fs::read(p).map_err(|e| {
                RitualError::CeremonyInvalid(format!("read ceremony {}: {e}", p.display()))
            })?;
            Ok::<_, RitualError>(format!("sha256:{}", ddf::sha256::sha256_hex(&bytes)))
        })
        .transpose()?;

    let extra: Vec<(&str, &str)> = vec![
        ("proposal_id", proposal_id),
        ("tool_id", tool_id),
        ("ritual_id", "ao-0003"),
        ("schema", "1"),
        ("effect_class", if external { "external" } else { "ledger_only" }),
    ];

    let owned: Vec<(String, String)> = ceremony_hash
        .map(|h| vec![("ceremony_content_sha256".to_string(), h)])
        .unwrap_or_default();

    append_shell_event(
        &ledger,
        &doctrine,
        RitualKind::Act.event_name(),
        APP_VERSION,
        "agent act recorded",
        domain,
        true,
        true,
        false,
        true,
        &extra,
        &owned,
        &[("external_effect", external)],
    )
    .map_err(RitualError::from)
}

/// `agent.reflect` — learning loop closure.
pub fn ritual_reflect(
    cfg: &AoConfig,
    proposal_id: &str,
    notes: &str,
    domain: &str,
) -> Result<String, RitualError> {
    require_engine_ok(cfg)?;
    let ledger = cfg.shell_ledger_path();
    let doctrine = cfg.engine_doctrine_path();
    append_shell_event(
        &ledger,
        &doctrine,
        RitualKind::Reflect.event_name(),
        APP_VERSION,
        "agent reflection recorded",
        domain,
        true,
        true,
        false,
        true,
        &[
            ("proposal_id", proposal_id),
            ("notes", notes),
            ("ritual_id", "ao-0004"),
            ("schema", "1"),
        ],
        &[],
        &[],
    )
    .map_err(RitualError::from)
}

/// `agent.simulate` — Phase 6 stub: records intent only; no mutation of engine sim contracts yet.
pub fn ritual_simulate(
    cfg: &AoConfig,
    proposal_id: &str,
    scenario_id: &str,
    domain: &str,
) -> Result<String, RitualError> {
    require_engine_ok(cfg)?;
    let ledger = cfg.shell_ledger_path();
    let doctrine = cfg.engine_doctrine_path();
    append_shell_event(
        &ledger,
        &doctrine,
        RitualKind::Simulate.event_name(),
        APP_VERSION,
        "simulation stub (Phase 6)",
        domain,
        true,
        true,
        true,
        true,
        &[
            ("proposal_id", proposal_id),
            ("scenario_id", scenario_id),
            ("phase", "6-stub"),
            ("ritual_id", "ao-0005"),
            ("schema", "1"),
        ],
        &[],
        &[("simulation_stub", true)],
    )
    .map_err(RitualError::from)
}
