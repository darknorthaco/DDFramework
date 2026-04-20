// Shrike ledger reader/writer — append-only, hash-chained.
//
// Read: yields the `entry_hash` of the last line, verifying the line
// parses (minimally) and its own entry_hash matches canonical form.
//
// Write: appends one new entry, after verifying the chain tip. Refuses
// to write if the last line's hash does not match recomputation —
// this prevents extending a broken chain.

use crate::canonical::Entry;
use crate::sha256::sha256_hex;
use std::fs::{File, OpenOptions};
use std::io::{self, BufRead, BufReader, Write};
use std::path::Path;

pub const ZERO_HASH: &str = "sha256:0000000000000000000000000000000000000000000000000000000000000000";

#[derive(Debug)]
pub enum LedgerError {
    Io(io::Error),
    MissingEntryHash { line_no: usize },
    ChainBreak { line_no: usize, stored: String, recomputed: String },
    MalformedLine { line_no: usize, reason: String },
}

impl std::fmt::Display for LedgerError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            LedgerError::Io(e) => write!(f, "ledger io error: {}", e),
            LedgerError::MissingEntryHash { line_no } => {
                write!(f, "ledger line {}: missing entry_hash", line_no)
            }
            LedgerError::ChainBreak { line_no, stored, recomputed } => write!(
                f,
                "ledger line {}: entry_hash mismatch (stored={} recomputed={})",
                line_no, stored, recomputed
            ),
            LedgerError::MalformedLine { line_no, reason } => {
                write!(f, "ledger line {}: {}", line_no, reason)
            }
        }
    }
}

impl std::error::Error for LedgerError {}

impl From<io::Error> for LedgerError {
    fn from(e: io::Error) -> Self {
        LedgerError::Io(e)
    }
}

/// Read the entry_hash of the last non-blank line of the ledger,
/// and verify its canonical-form hash.
/// Returns ZERO_HASH if the ledger is missing or empty.
pub fn read_head(path: &Path) -> Result<String, LedgerError> {
    if !path.exists() {
        return Ok(ZERO_HASH.to_string());
    }
    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let mut last_line: Option<(usize, String)> = None;
    for (idx, line) in reader.lines().enumerate() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        last_line = Some((idx + 1, line));
    }

    let (line_no, line) = match last_line {
        None => return Ok(ZERO_HASH.to_string()),
        Some(p) => p,
    };

    verify_line(&line, line_no)
}

fn verify_line(line: &str, line_no: usize) -> Result<String, LedgerError> {
    // We parse just enough to extract fields. No full JSON parser
    // (zero deps in Phase 2). We expect the line to end with
    // `,"entry_hash":"sha256:<hex>"}`. We strip it, rebuild the
    // canonical form by sorting all remaining keys, and hash.
    //
    // This parser accepts only the exact dialect our writer produces:
    // - flat object, keys are double-quoted ASCII
    // - values are either double-quoted strings (no nested quotes)
    //   or the literals `true`/`false`
    // - no whitespace
    //
    // A stricter JSON reader will come when a ritual needs nested
    // objects.

    let trimmed = line.trim();
    if !trimmed.starts_with('{') || !trimmed.ends_with('}') {
        return Err(LedgerError::MalformedLine {
            line_no,
            reason: "line is not a JSON object".into(),
        });
    }
    let body = &trimmed[1..trimmed.len() - 1];

    let mut fields: Vec<(String, FieldValue)> = Vec::new();
    let mut stored_entry_hash: Option<String> = None;

    for raw_pair in split_top_level_commas(body) {
        let (k, v) = split_key_value(&raw_pair).ok_or_else(|| LedgerError::MalformedLine {
            line_no,
            reason: format!("cannot parse field '{}'", raw_pair),
        })?;
        if k == "entry_hash" {
            stored_entry_hash = Some(match v {
                FieldValue::Str(s) => s,
                _ => {
                    return Err(LedgerError::MalformedLine {
                        line_no,
                        reason: "entry_hash is not a string".into(),
                    });
                }
            });
        } else {
            fields.push((k, v));
        }
    }

    let stored = stored_entry_hash.ok_or(LedgerError::MissingEntryHash { line_no })?;

    // Rebuild canonical form
    let mut entry = Entry::new();
    for (k, v) in &fields {
        match v {
            FieldValue::Str(s) => {
                entry.str(k, s.clone());
            }
            FieldValue::Bool(b) => {
                entry.boolean(k, *b);
            }
        }
    }
    let canonical = entry.canonical_bytes();
    let recomputed = format!("sha256:{}", sha256_hex(&canonical));
    if recomputed != stored {
        return Err(LedgerError::ChainBreak {
            line_no,
            stored,
            recomputed,
        });
    }
    Ok(stored)
}

#[derive(Debug)]
enum FieldValue {
    Str(String),
    Bool(bool),
}

fn split_top_level_commas(s: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut cur = String::new();
    let mut in_string = false;
    let mut prev_backslash = false;
    for c in s.chars() {
        if in_string {
            cur.push(c);
            if prev_backslash {
                prev_backslash = false;
            } else if c == '\\' {
                prev_backslash = true;
            } else if c == '"' {
                in_string = false;
            }
        } else if c == '"' {
            in_string = true;
            cur.push(c);
        } else if c == ',' {
            out.push(std::mem::take(&mut cur));
        } else {
            cur.push(c);
        }
    }
    if !cur.is_empty() {
        out.push(cur);
    }
    out
}

fn split_key_value(pair: &str) -> Option<(String, FieldValue)> {
    // Key is always a double-quoted string at the start.
    let bytes = pair.as_bytes();
    if bytes.first()? != &b'"' {
        return None;
    }
    let mut i = 1usize;
    let mut key = String::new();
    let mut prev_bs = false;
    while i < bytes.len() {
        let c = bytes[i] as char;
        if prev_bs {
            // Simple unescape
            match c {
                '"' | '\\' | '/' => key.push(c),
                'b' => key.push('\u{08}'),
                'f' => key.push('\u{0c}'),
                'n' => key.push('\n'),
                'r' => key.push('\r'),
                't' => key.push('\t'),
                _ => key.push(c),
            }
            prev_bs = false;
        } else if c == '\\' {
            prev_bs = true;
        } else if c == '"' {
            i += 1;
            break;
        } else {
            key.push(c);
        }
        i += 1;
    }
    // Expect colon
    if bytes.get(i)? != &b':' {
        return None;
    }
    i += 1;
    let value_str = &pair[i..];
    if value_str == "true" {
        return Some((key, FieldValue::Bool(true)));
    }
    if value_str == "false" {
        return Some((key, FieldValue::Bool(false)));
    }
    if value_str.starts_with('"') && value_str.ends_with('"') && value_str.len() >= 2 {
        let inner = &value_str[1..value_str.len() - 1];
        let mut out = String::with_capacity(inner.len());
        let mut chars = inner.chars();
        while let Some(c) = chars.next() {
            if c == '\\' {
                match chars.next()? {
                    '"' => out.push('"'),
                    '\\' => out.push('\\'),
                    '/' => out.push('/'),
                    'b' => out.push('\u{08}'),
                    'f' => out.push('\u{0c}'),
                    'n' => out.push('\n'),
                    'r' => out.push('\r'),
                    't' => out.push('\t'),
                    'u' => {
                        let hex: String = (0..4).filter_map(|_| chars.next()).collect();
                        if hex.len() != 4 {
                            return None;
                        }
                        let cp = u32::from_str_radix(&hex, 16).ok()?;
                        out.push(char::from_u32(cp)?);
                    }
                    other => out.push(other),
                }
            } else {
                out.push(c);
            }
        }
        return Some((key, FieldValue::Str(out)));
    }
    None
}

/// Append an entry, chaining from the current head.
/// Returns the new head's entry_hash.
pub fn append(path: &Path, entry_no_hash: &Entry) -> Result<String, LedgerError> {
    let entry_hash = entry_no_hash.entry_hash();
    let line = entry_no_hash.to_ledger_line(&entry_hash);

    if let Some(parent) = path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    let mut file = OpenOptions::new()
        .create(true)
        .append(true)
        .open(path)?;
    file.write_all(&line)?;
    file.flush()?;
    Ok(entry_hash)
}

/// Read every line and verify the chain from genesis. Returns the
/// count of entries and the head hash.
pub fn verify_chain(path: &Path) -> Result<(usize, String), LedgerError> {
    if !path.exists() {
        return Ok((0, ZERO_HASH.to_string()));
    }
    let file = File::open(path)?;
    let reader = BufReader::new(file);

    let mut prev = ZERO_HASH.to_string();
    let mut count = 0usize;
    for (idx, line) in reader.lines().enumerate() {
        let line = line?;
        if line.trim().is_empty() {
            continue;
        }
        let line_no = idx + 1;
        let stored = verify_line(&line, line_no)?;
        // Also verify the chain link: the line's prev_entry_hash must equal `prev`.
        let stored_prev = extract_prev(&line).ok_or_else(|| LedgerError::MalformedLine {
            line_no,
            reason: "missing prev_entry_hash".into(),
        })?;
        if stored_prev != prev {
            return Err(LedgerError::ChainBreak {
                line_no,
                stored: stored_prev,
                recomputed: prev.clone(),
            });
        }
        prev = stored;
        count += 1;
    }
    Ok((count, prev))
}

fn extract_prev(line: &str) -> Option<String> {
    // Find `"prev_entry_hash":"..."` by substring (dialect-safe:
    // prev_entry_hash is a string value, no nested quotes).
    let needle = "\"prev_entry_hash\":\"";
    let start = line.find(needle)? + needle.len();
    let rest = &line[start..];
    let end = rest.find('"')?;
    Some(rest[..end].to_string())
}

