// Stdlib-only RFC 3339 UTC timestamp formatter.
//
// Accepts a Unix epoch seconds count and produces
// "YYYY-MM-DDTHH:MM:SSZ".
// Civil-from-days algorithm adapted from Howard Hinnant's date
// library (public domain).

use std::time::{SystemTime, UNIX_EPOCH};

pub fn now_rfc3339() -> String {
    let secs = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_secs())
        .unwrap_or(0);
    unix_to_rfc3339(secs as i64)
}

pub fn unix_to_rfc3339(secs: i64) -> String {
    let days = secs.div_euclid(86400);
    let time_of_day = secs.rem_euclid(86400);
    let hour = time_of_day / 3600;
    let min = (time_of_day % 3600) / 60;
    let sec = time_of_day % 60;

    let (y, m, d) = civil_from_days(days);
    format!(
        "{:04}-{:02}-{:02}T{:02}:{:02}:{:02}Z",
        y, m, d, hour, min, sec
    )
}

fn civil_from_days(z_in: i64) -> (i64, u32, u32) {
    let z = z_in + 719468;
    let era = if z >= 0 { z } else { z - 146096 } / 146097;
    let doe = z - era * 146097;
    let yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
    let y = yoe + era * 400;
    let doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
    let mp = (5 * doy + 2) / 153;
    let d = (doy - (153 * mp + 2) / 5 + 1) as u32;
    let m = if mp < 10 { mp + 3 } else { mp - 9 } as u32;
    let y = if m <= 2 { y + 1 } else { y };
    (y, m, d)
}
