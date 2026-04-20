# Shrike — root build entry point.
#
# Pure POSIX make targets. No GNU-Make-isms where avoidable.
# All recipes must pass the 100-year test (LANGUAGES.md §2).

.POSIX:

PYTHON         ?= python
CARGO          ?= cargo
LEDGER         ?= ledger/events.jsonl

# ghost is not installed as a wheel in Phase 2; it's run from source.
# Set PYTHONPATH so `python -m ghost` resolves without `pip install`.
PYTHONPATH     := ghost-observer
export PYTHONPATH

# Deterministic builds: export SOURCE_DATE_EPOCH from the latest
# commit timestamp so two clean checkouts at the same commit produce
# byte-identical binaries. Falls back to a fixed date if git is
# unavailable.
SOURCE_DATE_EPOCH := $(shell git log -1 --pretty=%ct 2>/dev/null || echo 1745107200)
export SOURCE_DATE_EPOCH

.PHONY: help build verify verify-ledger test clean doctrine ghost

help:
	@echo "Shrike - Makefile targets"
	@echo ""
	@echo "  make build          Build phantom-core and hyperion-net (release)"
	@echo "  make verify         Run phantom verify (requires build first)"
	@echo "  make verify-ledger  Audit ledger/events.jsonl hash chain (pure Python)"
	@echo "  make test           Run all tests (cargo + python)"
	@echo "  make doctrine       Print embedded doctrine hashes from phantom"
	@echo "  make ghost          Run ghost-observer ledger summary (read-only)"
	@echo "  make ghost-advise   Run GHOST advisor (read-only on ledger; writes advisories)"
	@echo "  make ghost-verify   Verify advisory stream hash chain"
	@echo "  make clean          Remove target/ and python caches"
	@echo ""
	@echo "  SOURCE_DATE_EPOCH = $(SOURCE_DATE_EPOCH)"

build:
	$(CARGO) build --release --workspace

# `cargo run` locates the built binary without assuming the target
# directory path. This keeps the Makefile portable across environments
# that redirect CARGO_TARGET_DIR (CI caches, sandboxes, etc.).
verify: build
	$(CARGO) run --release --quiet --bin phantom -- verify

doctrine: build
	$(CARGO) run --release --quiet --bin phantom -- doctrine

verify-ledger:
	$(PYTHON) tools/verify_ledger.py $(LEDGER)

ghost:
	$(PYTHON) -m ghost $(LEDGER)

ghost-advise:
	$(PYTHON) -m ghost advise

ghost-verify:
	$(PYTHON) -m ghost verify-advisories

test:
	$(CARGO) test --workspace --release --lib --tests
	$(PYTHON) -m unittest discover -s ghost-observer -v

clean:
	$(CARGO) clean
	rm -rf ghost-observer/__pycache__ ghost-observer/ghost/__pycache__ \
	       ghost-observer/tests/__pycache__ tools/__pycache__
