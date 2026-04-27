//! `ca-shell` — CLI for the Constitutional Agent Shell (application rituals only).

use std::path::PathBuf;

use ca_shell::config::{default_shell_root, read_engine_root, AoConfig};
use ca_shell::kernel;
use ca_shell::rituals::{self, ActEffectClass};

fn main() {
    if let Err(e) = run() {
        eprintln!("ca-shell: {e}");
        std::process::exit(1);
    }
}

fn run() -> Result<(), String> {
    let mut args = std::env::args().skip(1).collect::<Vec<_>>();
    let cmd = args.first().cloned().unwrap_or_else(|| "help".into());
    if cmd == "help" || cmd == "--help" || cmd == "-h" {
        print_help();
        return Ok(());
    }

    // Global flags (simple parser): --shell-root <path>
    let mut shell_root_opt: Option<PathBuf> = None;
    let mut i = 0;
    while i < args.len() {
        if args[i] == "--shell-root" {
            let val = args
                .get(i + 1)
                .ok_or("--shell-root requires a path")?
                .clone();
            shell_root_opt = Some(PathBuf::from(val));
            args.remove(i);
            args.remove(i);
            continue;
        }
        i += 1;
    }

    let shell_root = default_shell_root(shell_root_opt)?;
    let engine_root = read_engine_root(&shell_root)?;
    let cfg = AoConfig::new(shell_root, engine_root);

    match cmd.as_str() {
        "engine-verify" => {
            let st = kernel::engine_verify(&cfg.engine_root)
                .map_err(|e| format!("spawn: {e}"))?;
            if !st.success() {
                return Err(format!("phantom verify exited {st}"));
            }
            println!("engine verify: ok");
        }
        "engine-advise" => {
            let st = kernel::engine_advise(&cfg.engine_root)
                .map_err(|e| format!("spawn: {e}"))?;
            if !st.success() {
                return Err(format!("ghost advise exited {st}"));
            }
            println!("engine advise: ok");
        }
        "propose" => {
            let proposal_id = take_flag(&mut args, "--proposal-id")?;
            let summary = take_flag(&mut args, "--summary")?;
            let domain = optional_flag(&mut args, "--domain", "complicated");
            let h = rituals::ritual_propose(&cfg, &proposal_id, &summary, &domain)
                .map_err(|e| e.to_string())?;
            println!("appended agent.propose entry_hash={h}");
        }
        "evaluate" => {
            let proposal_id = take_flag(&mut args, "--proposal-id")?;
            let verdict = take_flag(&mut args, "--verdict")?;
            let domain = optional_flag(&mut args, "--domain", "complicated");
            let h = rituals::ritual_evaluate(&cfg, &proposal_id, &verdict, &domain)
                .map_err(|e| e.to_string())?;
            println!("appended agent.evaluate entry_hash={h}");
        }
        "act" => {
            let proposal_id = take_flag(&mut args, "--proposal-id")?;
            let tool_id = take_flag(&mut args, "--tool-id")?;
            let effect = match take_flag(&mut args, "--effect").unwrap_or_else(|_| "ledger_only".into())
                .as_str()
            {
                "external" => ActEffectClass::External,
                _ => ActEffectClass::LedgerOnly,
            };
            let ceremony = args
                .iter()
                .position(|a| a == "--ceremony")
                .and_then(|p| args.get(p + 1))
                .map(PathBuf::from);
            let domain = optional_flag(&mut args, "--domain", "complicated");
            let ceremony_ref = ceremony.as_deref();
            let h = rituals::ritual_act(&cfg, &proposal_id, &tool_id, effect, ceremony_ref, &domain)
                .map_err(|e| e.to_string())?;
            println!("appended agent.act entry_hash={h}");
        }
        "reflect" => {
            let proposal_id = take_flag(&mut args, "--proposal-id")?;
            let notes = take_flag(&mut args, "--notes")?;
            let domain = optional_flag(&mut args, "--domain", "complicated");
            let h = rituals::ritual_reflect(&cfg, &proposal_id, &notes, &domain)
                .map_err(|e| e.to_string())?;
            println!("appended agent.reflect entry_hash={h}");
        }
        "simulate" => {
            let proposal_id = take_flag(&mut args, "--proposal-id")?;
            let scenario_id = take_flag(&mut args, "--scenario-id")?;
            let domain = optional_flag(&mut args, "--domain", "complicated");
            let h = rituals::ritual_simulate(&cfg, &proposal_id, &scenario_id, &domain)
                .map_err(|e| e.to_string())?;
            println!("appended agent.simulate entry_hash={h}");
        }
        other => return Err(format!("unknown command '{other}' (try ca-shell help)")),
    }

    Ok(())
}

fn optional_flag(args: &mut Vec<String>, name: &str, default: &str) -> String {
    match take_flag(args, name) {
        Ok(s) => s,
        Err(_) => default.to_string(),
    }
}

fn take_flag(args: &mut Vec<String>, name: &str) -> Result<String, String> {
    let pos = args
        .iter()
        .position(|a| a == name)
        .ok_or_else(|| format!("missing {name}"))?;
    args.remove(pos);
    let v = args
        .get(pos)
        .cloned()
        .ok_or_else(|| format!("{name} requires a value"))?;
    args.remove(pos);
    Ok(v)
}

fn print_help() {
    println!(
        "\
Constitutional Agent Shell — ca-shell

Usage:
  ca-shell [--shell-root <dir>] <command> [flags]

Commands:
  engine-verify     Run `phantom verify` in the engine checkout (kernel path).
  engine-advise     Run `python -m ghost advise` in the engine checkout.
  propose           Record agent.propose on the shell ledger.
  evaluate          Record agent.evaluate (requires engine verify ok).
  act               Record agent.act (external requires --ceremony file with OPERATOR_APPROVED=1).
  reflect           Record agent.reflect.
  simulate          Record agent.simulate (Phase 6 stub).

Global:
  --shell-root PATH   AO workspace root (default: cwd if config/shell.toml exists).

Examples:
  ca-shell engine-verify
  ca-shell propose --proposal-id p1 --summary \"Draft plan\" --domain complicated
"
    );
}
