//! Constitutional Agent Shell — application runtime on the DDFramework kernel (`ddf`).
//!
//! All mutating agent steps are recorded as **ledger rituals** (application events)
//! on the shell ledger. Engine verification and advisories go through the kernel
//! API only (`ddf::verify`, `ddf::ghost::advise`).

pub mod config;
pub mod kernel;
pub mod ledger_record;
pub mod rituals;

pub use config::AoConfig;
pub use ledger_record::ShellLedgerError;
pub use rituals::{ActEffectClass, RitualError, RitualKind};
