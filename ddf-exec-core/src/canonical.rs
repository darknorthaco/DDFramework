// Shrike canonical JSON — RFC-8785-subset serializer.
//
// Scope: flat object with keys = ASCII strings, values in
// {string, bool}. Sufficient for Phase 2 ledger entries. A richer
// serializer (nested, numbers, arrays) may be added when a ritual
// actually needs it.
//
// Rules:
//   - Sorted keys (lexicographic, byte-wise)
//   - No whitespace
//   - UTF-8 output (ensure_ascii = false)
//   - JSON string escaping: \" \\ \b \f \n \r \t \u00XX for C0
//   - All other bytes pass through as valid UTF-8

use crate::sha256::sha256_hex;

#[derive(Clone, Debug)]
pub enum Value {
    Str(String),
    Bool(bool),
}

#[derive(Clone, Debug, Default)]
pub struct Entry {
    fields: Vec<(String, Value)>,
}

impl Entry {
    pub fn new() -> Self {
        Self { fields: Vec::new() }
    }

    pub fn str(&mut self, key: &str, value: impl Into<String>) -> &mut Self {
        self.fields.push((key.to_string(), Value::Str(value.into())));
        self
    }

    pub fn boolean(&mut self, key: &str, value: bool) -> &mut Self {
        self.fields.push((key.to_string(), Value::Bool(value)));
        self
    }

    /// Canonical form used for SHA-256 hashing.
    /// Sorted keys, no whitespace, UTF-8.
    pub fn canonical_bytes(&self) -> Vec<u8> {
        let mut sorted = self.fields.clone();
        sorted.sort_by(|a, b| a.0.cmp(&b.0));
        let mut out = Vec::with_capacity(256);
        serialize(&mut out, &sorted);
        out
    }

    /// Compute the entry_hash for this (unsigned) entry.
    /// Returns `sha256:<hex>`.
    pub fn entry_hash(&self) -> String {
        let canonical = self.canonical_bytes();
        format!("sha256:{}", sha256_hex(&canonical))
    }

    /// Produce the NDJSON line written to the ledger.
    /// Shape: all fields sorted, then `entry_hash` appended last for
    /// human readability. Terminated with `\n`.
    pub fn to_ledger_line(&self, entry_hash: &str) -> Vec<u8> {
        let mut sorted = self.fields.clone();
        sorted.sort_by(|a, b| a.0.cmp(&b.0));
        let mut with_hash = sorted;
        with_hash.push((
            "entry_hash".to_string(),
            Value::Str(entry_hash.to_string()),
        ));
        let mut out = Vec::with_capacity(512);
        serialize(&mut out, &with_hash);
        out.push(b'\n');
        out
    }
}

fn serialize(out: &mut Vec<u8>, fields: &[(String, Value)]) {
    out.push(b'{');
    for (i, (k, v)) in fields.iter().enumerate() {
        if i > 0 {
            out.push(b',');
        }
        write_string(out, k);
        out.push(b':');
        match v {
            Value::Str(s) => write_string(out, s),
            Value::Bool(true) => out.extend_from_slice(b"true"),
            Value::Bool(false) => out.extend_from_slice(b"false"),
        }
    }
    out.push(b'}');
}

fn write_string(out: &mut Vec<u8>, s: &str) {
    out.push(b'"');
    for c in s.chars() {
        match c {
            '"' => out.extend_from_slice(b"\\\""),
            '\\' => out.extend_from_slice(b"\\\\"),
            '\u{08}' => out.extend_from_slice(b"\\b"),
            '\u{0c}' => out.extend_from_slice(b"\\f"),
            '\n' => out.extend_from_slice(b"\\n"),
            '\r' => out.extend_from_slice(b"\\r"),
            '\t' => out.extend_from_slice(b"\\t"),
            c if (c as u32) < 0x20 => {
                let u = c as u32;
                out.extend_from_slice(format!("\\u{:04x}", u).as_bytes());
            }
            c => {
                let mut buf = [0u8; 4];
                let encoded = c.encode_utf8(&mut buf);
                out.extend_from_slice(encoded.as_bytes());
            }
        }
    }
    out.push(b'"');
}
