#!/usr/bin/env python3
"""Convert climbing_centers.csv into climbing_centers.json.

Coerces types (booleans, floats), drops blank values to null, validates the
grading_type enum, derives an IANA `timezone` for each located center from its
coordinates (offline, via timezonefinder), and fails loudly on bad data so a
broken edit never reaches the published JSON.

The timezone is DERIVED here, not stored in the CSV: humans edit coordinates,
the build bakes the matching IANA id into the JSON. The app reads it to decide
"open now" in each gym's own local time.
"""

import csv
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "climbing_centers.csv"
OUT = ROOT / "climbing_centers.json"

SCHEMA_VERSION = 2  # bumped: records now carry a derived `timezone`

BOOL_FIELDS = {
    "bouldering", "lead", "top_rope",
    "moonboard", "kilterboard", "spraywall",
}
FLOAT_FIELDS = {"latitude", "longitude"}

# Closed vocabulary. Blank is allowed (means "not yet recorded") and maps to
# null. Any other value is a hard error.
GRADING_TYPES = {"color", "font", "v", "none"}


def coerce(key, value):
    value = (value or "").strip()
    if value == "":
        return None
    if key in BOOL_FIELDS:
        low = value.lower()
        if low not in ("true", "false"):
            raise ValueError(f"{key!r} must be true/false, got {value!r}")
        return low == "true"
    if key in FLOAT_FIELDS:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"{key!r} must be a number, got {value!r}")
    return value


def validate(row, line_no, errors):
    gid = row.get("id")
    if not gid:
        errors.append(f"row {line_no}: missing id")

    gt = row.get("grading_type")
    if gt is not None and gt not in GRADING_TYPES:
        errors.append(
            f"row {line_no} (id={gid}): grading_type {gt!r} not in "
            f"{sorted(GRADING_TYPES)}"
        )

    lat, lng = row.get("latitude"), row.get("longitude")
    if (lat is None) != (lng is None):
        errors.append(
            f"row {line_no} (id={gid}): latitude/longitude must both be set "
            f"or both blank"
        )


def main():
    if not SRC.exists():
        print(f"error: {SRC} not found", file=sys.stderr)
        return 1

    try:
        from timezonefinder import TimezoneFinder
    except ImportError:
        print("error: timezonefinder not installed (pip install -r requirements.txt)",
              file=sys.stderr)
        return 1
    tf = TimezoneFinder()

    with SRC.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        raw_rows = list(reader)

    centers = []
    errors = []
    warnings = []
    seen_ids = set()

    for i, raw in enumerate(raw_rows, start=2):  # line 1 is the header
        try:
            row = {k: coerce(k, v) for k, v in raw.items()}
        except ValueError as e:
            errors.append(f"row {i}: {e}")
            continue

        validate(row, i, errors)

        gid = row.get("id")
        if gid in seen_ids:
            errors.append(f"row {i}: duplicate id {gid!r}")
        seen_ids.add(gid)

        # Derive the IANA timezone from the coordinates. A located center that
        # resolves to nothing (point just offshore, etc.) is a soft warning, not
        # a failure -- the app falls back to the device timezone.
        lat, lng = row.get("latitude"), row.get("longitude")
        if lat is not None and lng is not None:
            tz = tf.timezone_at(lat=lat, lng=lng)
            if tz is None:
                warnings.append(f"row {i} (id={gid}): no timezone for {lat},{lng}")
            row["timezone"] = tz
        else:
            row["timezone"] = None

        centers.append(row)

    for w in warnings:
        print(f"  warning: {w}", file=sys.stderr)

    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    centers.sort(key=lambda c: (c.get("country") or "", c.get("city") or "",
                                c.get("gym_name") or ""))

    payload = {
        "version": SCHEMA_VERSION,
        "count": len(centers),
        "centers": centers,
    }

    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(centers)} centers to {OUT.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
