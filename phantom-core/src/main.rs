// phantom — Shrike Phantom Core CLI.
//
// Subcommands (Phase 2):
//   phantom --version     Print version and embedded doctrine hashes
//   phantom doctrine      Print both doctrine versions + hashes + ledger path
//   phantom verify        Verify doctrine hashes match on-disk files,
//                         append a verify.result entry to the ledger.
//
// Invariants enforced here:
//   I4 — reproducible build (release profile pinned, zero deps)
//   I5 — explicit arguments (no env reads beyond cwd for the root)
//   I6 — doctrine-as-code (embedded hashes vs. on-disk hashes)
//   I7 — no silent mutation (ledger entry is written BEFORE the
//        process exits non-zero on mismatch)

use phantom_core::canonical::Entry;
use phantom_core::ledger::{self, ZERO_HASH};
use phantom_core::sha256::sha256_hex;
use phantom_core::timestamp::now_rfc3339;
use phantom_core::{
    CONSTELLATION_HASH_EMBEDDED, CONSTELLATION_VERSION, DOCTRINE_HASH_EMBEDDED, DOCTRINE_VERSION,
};

use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::ExitCode;

const LEDGER_RELATIVE: &str = "ledger/events.jsonl";
const DOCTRINE_RELATIVE: &str = "doctrine.toml";
const CONSTELLATION_RELATIVE: &str = "constellation.toml";

fn main() -> ExitCode {
    let args: Vec<String> = env::args().collect();
    let cmd = args.get(1).map(String::as_str).unwrap_or("help");

    // Per invariant I5, --root is the one declared env input.
    let root = parse_root(&args).unwrap_or_else(|| PathBuf::from("."));

    match cmd {
        "--version" | "version" | "-V" => {
            print_version();
            ExitCode::SUCCESS
        }
        "doctrine" => {
            print_doctrine(&root);
            ExitCode::SUCCESS
        }
        "verify" => match run_verify(&root) {
            Ok(code) => code,
            Err(e) => {
                eprintln!("phantom verify: fatal: {}", e);
                ExitCode::from(3)
            }
        },
        "help" | "--help" | "-h" => {
            print_help();
            ExitCode::SUCCESS
        }
        other => {
            eprintln!("phantom: unknown subcommand: {}", other);
            print_help();
            ExitCode::from(2)
        }
    }
}

fn parse_root(args: &[String]) -> Option<PathBuf> {
    let mut it = args.iter();
    while let Some(a) = it.next() {
        if a == "--root" {
            if let Some(v) = it.next() {
                return Some(PathBuf::from(v));
            }
        }
    }
    None
}

fn print_help() {
    println!(
        "phantom — Shrike Phantom Core v{}\n\n\
        Usage: phantom <subcommand> [--root <path>]\n\n\
        Subcommands:\n  \
            verify     Verify doctrine hashes and append a ledger entry\n  \
            doctrine   Print embedded doctrine hashes + versions\n  \
            version    Print binary version and hashes\n  \
            help       Show this help\n",
        DOCTRINE_VERSION
    );
}

fn print_version() {
    println!("phantom {}", DOCTRINE_VERSION);
    println!("  doctrine_version       = {}", DOCTRINE_VERSION);
    println!("  constitution_version   = {}", CONSTELLATION_VERSION);
    println!("  embedded doctrine      = {}", DOCTRINE_HASH_EMBEDDED);
    println!("  embedded constellation = {}", CONSTELLATION_HASH_EMBEDDED);
}

fn print_doctrine(root: &Path) {
    println!("phantom doctrine");
    println!("  root                   = {}", root.display());
    println!("  doctrine_version       = {}", DOCTRINE_VERSION);
    println!("  constitution_version   = {}", CONSTELLATION_VERSION);
    println!("  embedded doctrine      = {}", DOCTRINE_HASH_EMBEDDED);
    println!("  embedded constellation = {}", CONSTELLATION_HASH_EMBEDDED);
    println!("  doctrine file          = {}", root.join(DOCTRINE_RELATIVE).display());
    println!("  constellation file     = {}", root.join(CONSTELLATION_RELATIVE).display());
    println!("  ledger file            = {}", root.join(LEDGER_RELATIVE).display());
}

fn run_verify(root: &Path) -> Result<ExitCode, String> {
    let doctrine_path = root.join(DOCTRINE_RELATIVE);
    let constellation_path = root.join(CONSTELLATION_RELATIVE);
    let ledger_path = root.join(LEDGER_RELATIVE);

    let doctrine_bytes = fs::read(&doctrine_path)
        .map_err(|e| format!("cannot read {}: {}", doctrine_path.display(), e))?;
    let constellation_bytes = fs::read(&constellation_path)
        .map_err(|e| format!("cannot read {}: {}", constellation_path.display(), e))?;

    let doctrine_actual = format!("sha256:{}", sha256_hex(&doctrine_bytes));
    let constellation_actual = format!("sha256:{}", sha256_hex(&constellation_bytes));

    let doctrine_match = doctrine_actual == DOCTRINE_HASH_EMBEDDED;
    let constellation_match = constellation_actual == CONSTELLATION_HASH_EMBEDDED;
    let status: &str = match (doctrine_match, constellation_match) {
        (true, true) => "ok",
        (false, true) => "doctrine-mismatch",
        (true, false) => "constellation-mismatch",
        (false, false) => "both-mismatch",
    };

    let prev = ledger::read_head(&ledger_path).map_err(|e| format!("ledger head: {}", e))?;
    if prev == ZERO_HASH {
        eprintln!("phantom verify: ledger empty; this will be the genesis entry.");
    }

    let mut entry = Entry::new();
    entry
        .str("timestamp", now_rfc3339())
        .str("event", "verify.result")
        .str("version", DOCTRINE_VERSION)
        .str(
            "change",
            format!(
                "phantom verify — status={} (doctrine match={}, constellation match={})",
                status, doctrine_match, constellation_match
            ),
        )
        .str("domain", "complicated")
        .boolean("integrity_check", true)
        .boolean("regenerative_check", true)
        .boolean("simulation_required", false)
        .boolean("disruption_considered", false)
        .str("doctrine_hash", doctrine_actual.clone())
        .str("constellation_hash", constellation_actual.clone())
        .str("status", status)
        .str("prev_entry_hash", prev);

    // Invariant I7: write the ledger entry BEFORE we allow a
    // mismatch to make the process exit non-zero.
    let entry_hash = ledger::append(&ledger_path, &entry)
        .map_err(|e| format!("ledger append: {}", e))?;

    println!("phantom verify");
    println!("  status                 = {}", status);
    println!("  doctrine     match     = {}", doctrine_match);
    println!("  constellation match    = {}", constellation_match);
    println!("  doctrine_hash (actual) = {}", doctrine_actual);
    println!("  constellation (actual) = {}", constellation_actual);
    println!("  embedded doctrine      = {}", DOCTRINE_HASH_EMBEDDED);
    println!("  embedded constellation = {}", CONSTELLATION_HASH_EMBEDDED);
    println!("  ledger entry_hash      = {}", entry_hash);

    if status == "ok" {
        Ok(ExitCode::SUCCESS)
    } else {
        eprintln!("phantom verify: FAIL — {}", status);
        Ok(ExitCode::from(1))
    }
}
