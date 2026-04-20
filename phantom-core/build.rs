// Shrike phantom-core build script.
//
// At build time, reads ../doctrine.toml and ../constellation.toml,
// computes their SHA-256, and emits the hex digests as compile-time
// env vars consumed by src/main.rs. Enforces invariant I6
// (doctrine-as-code): the binary knows the hash of the doctrine it
// was built against and will refuse to run if the on-disk doctrine
// does not match.
//
// This script re-uses src/sha256.rs via `include!` so the hashing
// code is identical in build and runtime.

use std::fs;
use std::path::Path;

include!("src/sha256.rs");

fn read_and_hash(path: &Path) -> String {
    let bytes = fs::read(path)
        .unwrap_or_else(|e| panic!("phantom-core build: cannot read {}: {}", path.display(), e));
    sha256_hex(&bytes)
}

fn main() {
    let doctrine_path = Path::new("../doctrine.toml");
    let constellation_path = Path::new("../constellation.toml");

    let doctrine_hash = read_and_hash(doctrine_path);
    let constellation_hash = read_and_hash(constellation_path);

    println!("cargo:rustc-env=SHRIKE_DOCTRINE_HASH=sha256:{}", doctrine_hash);
    println!(
        "cargo:rustc-env=SHRIKE_CONSTELLATION_HASH=sha256:{}",
        constellation_hash
    );

    println!("cargo:rerun-if-changed=../doctrine.toml");
    println!("cargo:rerun-if-changed=../constellation.toml");
    println!("cargo:rerun-if-changed=src/sha256.rs");
    println!("cargo:rerun-if-changed=build.rs");
}
