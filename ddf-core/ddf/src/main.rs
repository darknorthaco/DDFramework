//! ddf CLI — DDFramework Kernel command-line interface.
//!
//! Thin dispatcher. Subcommands delegate to the underlying `phantom`
//! binary (for ledger-writing rituals) or to the `ghost-observer`
//! Python package (for the advisor and verify-advisories).
//!
//! Behavior contract: `ddf verify` MUST produce results identical to
//! `phantom verify`. Tests enforce this.

use std::env;
use std::process::{Command, ExitCode};

use ddf::{phantom_bin_path, API_VERSION, ENGINE_VERSION};

const PHANTOM_FORWARDABLE: &[&str] = &[
    "verify",
    "doctrine",
    "amend-doctrine",
    "file-waiver",
    "version",
    "--version",
];

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    let cmd = args.get(1).map(String::as_str).unwrap_or("help");
    let rest: Vec<&str> = args.iter().skip(2).map(String::as_str).collect();

    match cmd {
        "help" | "--help" | "-h" => {
            print_help();
            ExitCode::SUCCESS
        }
        "ddf-version" => {
            println!("ddf {} (DDFramework engine v{})", API_VERSION, ENGINE_VERSION);
            ExitCode::SUCCESS
        }
        sub if PHANTOM_FORWARDABLE.contains(&sub) => forward_to_phantom(sub, &rest),
        "advise" => forward_to_python(&["-m", "ghost", "advise"]),
        "verify-advisories" => forward_to_python(&["-m", "ghost", "verify-advisories"]),
        "ledger" => {
            let mut py_args: Vec<&str> = vec!["-m", "ghost"];
            py_args.extend(rest.iter().copied());
            forward_to_python(&py_args)
        }
        "run-ritual" => run_ritual_cmd(&rest),
        other => {
            eprintln!("ddf: unknown subcommand '{}'", other);
            print_help();
            ExitCode::from(2)
        }
    }
}

fn forward_to_phantom(sub: &str, rest: &[&str]) -> ExitCode {
    let status = Command::new(phantom_bin_path())
        .arg(sub)
        .args(rest)
        .status();
    exit_code_from(status, "phantom")
}

fn forward_to_python(args: &[&str]) -> ExitCode {
    let python = env::var("DDF_PYTHON").unwrap_or_else(|_| "python".to_string());
    let mut cmd = Command::new(python);
    cmd.args(args);
    if env::var_os("PYTHONPATH").is_none() {
        cmd.env("PYTHONPATH", "ghost-observer");
    }
    exit_code_from(cmd.status(), "python")
}

fn run_ritual_cmd(rest: &[&str]) -> ExitCode {
    let id = match rest.first() {
        Some(s) => *s,
        None => {
            eprintln!("ddf run-ritual: missing ritual id");
            eprintln!("  known ids: 0001 / verify, 0006 / ghost-advise");
            return ExitCode::from(2);
        }
    };
    match id {
        "0001" | "verify" => forward_to_phantom("verify", &[]),
        "0006" | "ghost-advise" => forward_to_python(&["-m", "ghost", "advise"]),
        other => {
            eprintln!(
                "ddf run-ritual: ritual '{}' requires explicit arguments; use the specific \
                 subcommand (`ddf amend-doctrine`, `ddf file-waiver`).",
                other
            );
            ExitCode::from(2)
        }
    }
}

fn exit_code_from(status: std::io::Result<std::process::ExitStatus>, tool: &str) -> ExitCode {
    match status {
        Ok(s) => s
            .code()
            .and_then(|c| u8::try_from(c).ok())
            .map(ExitCode::from)
            .unwrap_or(ExitCode::SUCCESS),
        Err(e) => {
            eprintln!("ddf: failed to invoke {}: {}", tool, e);
            ExitCode::from(127)
        }
    }
}

fn print_help() {
    println!(
        "ddf - DDFramework Kernel CLI v{} (engine v{})\n",
        API_VERSION, ENGINE_VERSION
    );
    println!("Usage: ddf <subcommand> [args...]\n");
    println!("Rituals (delegate to phantom):");
    println!("  verify                 Run the verify ritual (same as `phantom verify`)");
    println!("  doctrine               Print embedded doctrine hashes + versions");
    println!("  amend-doctrine ...     Record a doctrine amendment");
    println!("  file-waiver ...        Record a waiver filing");
    println!("  run-ritual <id>        Run a registered zero-arg ritual by id");
    println!();
    println!("Observer (delegate to ghost):");
    println!("  advise                 Run the GHOST advisor (ritual 0006)");
    println!("  verify-advisories      Audit the advisory stream chain");
    println!("  ledger [path]          Show ledger summary");
    println!();
    println!("Meta:");
    println!("  ddf-version            Print ddf API version + engine version");
    println!("  help, --help           Show this help");
    println!();
    println!("Environment:");
    println!("  DDF_PHANTOM_BIN        Override phantom binary path");
    println!("  DDF_PYTHON             Override python interpreter");
    println!("  PYTHONPATH             Required to include ghost-observer (set automatically if unset)");
}
