// ddf-exec — DDFramework engine executor CLI (formerly phantom).
//
// Subcommands (Phase 2):
//   ddf-exec --version     Print version and embedded doctrine hashes
//   ddf-exec doctrine      Print both doctrine versions + hashes + ledger path
//   ddf-exec verify        Verify doctrine hashes match on-disk files,
//                         append a verify.result entry to the ledger.
//
// Invariants enforced here:
//   I4 — reproducible build (release profile pinned, zero deps)
//   I5 — explicit arguments (no env reads beyond cwd for the root)
//   I6 — doctrine-as-code (embedded hashes vs. on-disk hashes)
//   I7 — no silent mutation (ledger entry is written BEFORE the
//        process exits non-zero on mismatch)

use ddf_exec_core::canonical::Entry;
use ddf_exec_core::ledger::{self, ZERO_HASH};
use ddf_exec_core::sha256::sha256_hex_file_normalized;
use ddf_exec_core::timestamp::now_rfc3339;
use ddf_exec_core::{
    CONSTELLATION_HASH_EMBEDDED, CONSTELLATION_VERSION, DOCTRINE_HASH_EMBEDDED, DOCTRINE_VERSION,
};

use std::env;
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
                eprintln!("ddf-exec verify: fatal: {}", e);
                ExitCode::from(3)
            }
        },
        "amend-doctrine" => match run_amend_doctrine(&root, &args) {
            Ok(code) => code,
            Err(e) => {
                eprintln!("ddf-exec amend-doctrine: fatal: {}", e);
                ExitCode::from(3)
            }
        },
        "file-waiver" => match run_file_waiver(&root, &args) {
            Ok(code) => code,
            Err(e) => {
                eprintln!("ddf-exec file-waiver: fatal: {}", e);
                ExitCode::from(3)
            }
        },
        "help" | "--help" | "-h" => {
            print_help();
            ExitCode::SUCCESS
        }
        other => {
            eprintln!("ddf-exec: unknown subcommand: {}", other);
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
        "ddf-exec — DDFramework engine executor v{}\n\n\
        Usage: ddf-exec <subcommand> [--root <path>] [ritual flags...]\n\n\
        Subcommands:\n  \
            verify           Verify doctrine hashes and append ledger entry\n  \
            amend-doctrine   Record a doctrine amendment (requires --approve)\n  \
            file-waiver      Record a waiver filing (requires --approve)\n  \
            doctrine         Print embedded doctrine hashes + versions\n  \
            version          Print binary version and hashes\n  \
            help             Show this help\n\n\
        amend-doctrine flags:\n  \
            --version <v>          New doctrine version (SemVer)\n  \
            --rationale <text>     Written rationale (required)\n  \
            --domain <cynefin>     obvious|complicated|complex|chaotic\n  \
            --approve              Human-architect approval gate (required)\n\n\
        file-waiver flags:\n  \
            --id <W-id>            Waiver id from WAIVERS.md\n  \
            --waiver <path>        Path to waiver manifest\n  \
            --approve              Human-architect approval gate (required)\n",
        DOCTRINE_VERSION
    );
}

fn print_version() {
    println!("ddf-exec {}", DOCTRINE_VERSION);
    println!("  doctrine_version       = {}", DOCTRINE_VERSION);
    println!("  constitution_version   = {}", CONSTELLATION_VERSION);
    println!("  embedded doctrine      = {}", DOCTRINE_HASH_EMBEDDED);
    println!("  embedded constellation = {}", CONSTELLATION_HASH_EMBEDDED);
}

fn print_doctrine(root: &Path) {
    println!("ddf-exec doctrine");
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

    // Use line-ending-normalized hashing so Windows and Unix agree.
    let doctrine_actual = format!(
        "sha256:{}",
        sha256_hex_file_normalized(&doctrine_path)
            .map_err(|e| format!("cannot read {}: {}", doctrine_path.display(), e))?
    );
    let constellation_actual = format!(
        "sha256:{}",
        sha256_hex_file_normalized(&constellation_path)
            .map_err(|e| format!("cannot read {}: {}", constellation_path.display(), e))?
    );

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
        eprintln!("ddf-exec verify: ledger empty; this will be the genesis entry.");
    }

    let mut entry = Entry::new();
    entry
        .str("timestamp", now_rfc3339())
        .str("event", "verify.result")
        .str("version", DOCTRINE_VERSION)
        .str(
            "change",
            format!(
                "ddf-exec verify — status={} (doctrine match={}, constellation match={})",
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

    println!("ddf-exec verify");
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
        eprintln!("ddf-exec verify: FAIL — {}", status);
        Ok(ExitCode::from(1))
    }
}

// ---------------------------------------------------------------------------
// amend-doctrine ritual (0004) — records a doctrine amendment ceremony.
// The ritual does NOT modify files; it RECORDS the ceremony of amendment.
// Operators edit DOCTRINE.md and doctrine.toml by hand; this ritual is the
// mandatory logging step (Constellation §9 + Shrike VII).
// ---------------------------------------------------------------------------

fn flag_value<'a>(args: &'a [String], name: &str) -> Option<&'a str> {
    let mut it = args.iter();
    while let Some(a) = it.next() {
        if a == name {
            return it.next().map(String::as_str);
        }
    }
    None
}

fn flag_present(args: &[String], name: &str) -> bool {
    args.iter().any(|a| a == name)
}

fn extract_string_field(line: &str, field: &str) -> Option<String> {
    let needle = format!("\"{}\":\"", field);
    let start = line.find(&needle)? + needle.len();
    let rest = &line[start..];
    let end = rest.find('"')?;
    Some(rest[..end].to_string())
}

/// Scan the ledger for the most recent doctrine-amendment-class entry
/// and return its `doctrine_hash` field. A "doctrine-amendment-class"
/// entry is one whose `event` is either `doctrine_amendment` (genesis
/// style) or `doctrine.amended` (ritual-produced style). Other entry
/// kinds — including verify.result — are ignored here so amend-doctrine
/// compares against the last CEREMONIAL amendment, not incidental
/// hash-recording events.
fn find_last_amendment_doctrine_hash(ledger_path: &Path) -> Option<String> {
    use std::io::BufRead;
    let file = std::fs::File::open(ledger_path).ok()?;
    let reader = std::io::BufReader::new(file);
    let mut last: Option<String> = None;
    for line in reader.lines().map_while(Result::ok) {
        let event = extract_string_field(&line, "event").unwrap_or_default();
        if event == "doctrine_amendment" || event == "doctrine.amended" {
            if let Some(h) = extract_string_field(&line, "doctrine_hash") {
                last = Some(h);
            }
        }
    }
    last
}

fn run_amend_doctrine(root: &Path, args: &[String]) -> Result<ExitCode, String> {
    let new_version = flag_value(args, "--version")
        .ok_or_else(|| "missing --version <SemVer>".to_string())?;
    let rationale = flag_value(args, "--rationale")
        .ok_or_else(|| "missing --rationale <text>".to_string())?;
    let domain = flag_value(args, "--domain").unwrap_or("complicated");
    let approved = flag_present(args, "--approve");

    if !approved {
        return Err(
            "refusing to record amendment without --approve (human-architect gate, Constellation §14)".into(),
        );
    }
    match domain {
        "obvious" | "complicated" | "complex" | "chaotic" => {}
        _ => {
            return Err(format!(
                "invalid --domain '{}'; must be one of obvious|complicated|complex|chaotic",
                domain
            ));
        }
    }

    let doctrine_path = root.join(DOCTRINE_RELATIVE);
    let constellation_path = root.join(CONSTELLATION_RELATIVE);
    let ledger_path = root.join(LEDGER_RELATIVE);

    let new_doctrine_hash = format!(
        "sha256:{}",
        sha256_hex_file_normalized(&doctrine_path)
            .map_err(|e| format!("cannot read {}: {}", doctrine_path.display(), e))?
    );
    let new_constellation_hash = format!(
        "sha256:{}",
        sha256_hex_file_normalized(&constellation_path)
            .map_err(|e| format!("cannot read {}: {}", constellation_path.display(), e))?
    );

    // Look up the previous doctrine hash from the most recent
    // doctrine-amendment ceremony (genesis or ritual-produced).
    // Other event kinds (e.g. verify.result) are ignored here so that
    // routine verification does not shadow the amendment timeline.
    let prev_doctrine_hash = find_last_amendment_doctrine_hash(&ledger_path)
        .unwrap_or_else(|| ZERO_HASH.to_string());

    if prev_doctrine_hash == new_doctrine_hash {
        return Err(format!(
            "no doctrine change detected (current doctrine_hash = {}). \
             Edit doctrine.toml / DOCTRINE.md before recording an amendment.",
            new_doctrine_hash
        ));
    }

    let prev_entry = ledger::read_head(&ledger_path).map_err(|e| format!("ledger head: {}", e))?;

    let mut entry = Entry::new();
    entry
        .str("timestamp", now_rfc3339())
        .str("event", "doctrine.amended")
        .str("version", new_version)
        .str(
            "change",
            format!(
                "Doctrine amended to {} — rationale: {}",
                new_version, rationale
            ),
        )
        .str("domain", domain)
        .boolean("integrity_check", true)
        .boolean("regenerative_check", true)
        .boolean("simulation_required", false)
        .boolean("disruption_considered", true)
        .str("doctrine_hash", new_doctrine_hash.clone())
        .str("constellation_hash", new_constellation_hash.clone())
        .str("previous_doctrine_hash", prev_doctrine_hash)
        .str("rationale", rationale)
        .boolean("human_approved", true)
        .str("prev_entry_hash", prev_entry);

    let entry_hash =
        ledger::append(&ledger_path, &entry).map_err(|e| format!("ledger append: {}", e))?;

    println!("ddf-exec amend-doctrine");
    println!("  new version            = {}", new_version);
    println!("  domain                 = {}", domain);
    println!("  new doctrine_hash      = {}", new_doctrine_hash);
    println!("  constellation_hash     = {}", new_constellation_hash);
    println!("  ledger entry_hash      = {}", entry_hash);
    Ok(ExitCode::SUCCESS)
}

// ---------------------------------------------------------------------------
// file-waiver ritual (0005) — records a waiver filing.
// Reads a waiver manifest (any plain-text file), hashes it, and records a
// ledger entry. Does NOT modify WAIVERS.md; operator is responsible for the
// registry edit. This ritual is the mandatory logging step.
// ---------------------------------------------------------------------------

fn run_file_waiver(root: &Path, args: &[String]) -> Result<ExitCode, String> {
    let waiver_id = flag_value(args, "--id")
        .ok_or_else(|| "missing --id <W-YYYYMMDD-NN>".to_string())?;
    let waiver_path_arg = flag_value(args, "--waiver")
        .ok_or_else(|| "missing --waiver <path>".to_string())?;
    let approved = flag_present(args, "--approve");

    if !approved {
        return Err(
            "refusing to record waiver without --approve (human-architect gate, Constellation §14)".into(),
        );
    }

    let waiver_path = PathBuf::from(waiver_path_arg);
    let waiver_bytes = std::fs::read(&waiver_path)
        .map_err(|e| format!("cannot read waiver file {}: {}", waiver_path.display(), e))?;
    let waiver_hash = format!(
        "sha256:{}",
        ddf_exec_core::sha256::sha256_hex(&ddf_exec_core::sha256::strip_cr(&waiver_bytes))
    );

    let doctrine_path = root.join(DOCTRINE_RELATIVE);
    let constellation_path = root.join(CONSTELLATION_RELATIVE);
    let ledger_path = root.join(LEDGER_RELATIVE);

    let doctrine_hash = format!(
        "sha256:{}",
        sha256_hex_file_normalized(&doctrine_path)
            .map_err(|e| format!("cannot read {}: {}", doctrine_path.display(), e))?
    );
    let constellation_hash = format!(
        "sha256:{}",
        sha256_hex_file_normalized(&constellation_path)
            .map_err(|e| format!("cannot read {}: {}", constellation_path.display(), e))?
    );

    let prev_entry = ledger::read_head(&ledger_path).map_err(|e| format!("ledger head: {}", e))?;

    let mut entry = Entry::new();
    entry
        .str("timestamp", now_rfc3339())
        .str("event", "waiver.filed")
        .str("version", DOCTRINE_VERSION)
        .str(
            "change",
            format!(
                "Waiver {} filed — manifest sha {}",
                waiver_id, waiver_hash
            ),
        )
        .str("domain", "complicated")
        .boolean("integrity_check", true)
        .boolean("regenerative_check", true)
        .boolean("simulation_required", false)
        .boolean("disruption_considered", true)
        .str("doctrine_hash", doctrine_hash)
        .str("constellation_hash", constellation_hash)
        .str("waiver_id", waiver_id)
        .str("waiver_path", waiver_path.to_string_lossy().to_string())
        .str("waiver_hash", waiver_hash.clone())
        .boolean("human_approved", true)
        .str("prev_entry_hash", prev_entry);

    let entry_hash =
        ledger::append(&ledger_path, &entry).map_err(|e| format!("ledger append: {}", e))?;

    println!("ddf-exec file-waiver");
    println!("  waiver_id              = {}", waiver_id);
    println!("  waiver_path            = {}", waiver_path.display());
    println!("  waiver_hash            = {}", waiver_hash);
    println!("  ledger entry_hash      = {}", entry_hash);
    Ok(ExitCode::SUCCESS)
}
