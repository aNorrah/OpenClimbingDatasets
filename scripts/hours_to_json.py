#!/usr/bin/env python3
"""Convert opening_hours.csv into opening_hours.json.

Per-day open/close pairs become a 7-element `days` array (index 0 = Monday ..
6 = Sunday; null = closed that day), in the shape the app's GymHoursDirectory
decodes. Validates HH:MM times and that each day's open/close are both-set or
both-blank (hard errors), and cross-checks every id against climbing_centers.csv
-- an "orphan" hours row (no matching center) is a WARNING, not a failure: the
JSON is still valid and the app simply never shows hours it can't pin to a gym,
but the warning surfaces the id mismatch so it can be reconciled.
"""

import csv
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "opening_hours.csv"
OUT = ROOT / "opening_hours.json"
CENTERS = ROOT / "climbing_centers.csv"

SCHEMA_VERSION = 1
DAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]  # index 0 = Monday
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
STATUS_VALUES = {"verified", "secondary", "unverified"}
CONFIDENCE_VALUES = {"high", "medium", "low"}


def clean(v):
    return (v or "").strip()


def center_ids():
    """The set of known center ids, or None when the file is absent (skip the
    orphan cross-check rather than fail)."""
    if not CENTERS.exists():
        return None
    with CENTERS.open(encoding="utf-8-sig", newline="") as f:
        return {clean(r.get("id")) for r in csv.DictReader(f)}


def main():
    if not SRC.exists():
        print(f"error: {SRC} not found", file=sys.stderr)
        return 1

    ids = center_ids()

    with SRC.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))

    hours = []
    errors = []
    warnings = []
    seen = set()

    for i, raw in enumerate(rows, start=2):  # line 1 is the header
        gid = clean(raw.get("id"))
        if not gid:
            errors.append(f"row {i}: missing id")
            continue
        if gid in seen:
            errors.append(f"row {i}: duplicate id {gid!r}")
        seen.add(gid)
        if ids is not None and gid not in ids:
            warnings.append(
                f"row {i} (id={gid}): no matching center in climbing_centers.csv "
                f"(orphan hours -- will not show in the app)"
            )

        days = []
        for d in DAYS:
            o, c = clean(raw.get(f"{d}_open")), clean(raw.get(f"{d}_close"))
            if not o and not c:
                days.append(None)
                continue
            if bool(o) != bool(c):
                errors.append(
                    f"row {i} (id={gid}): {d} has only one of open/close set "
                    f"(open={o!r} close={c!r})"
                )
                days.append(None)
                continue
            if not TIME_RE.match(o):
                errors.append(f"row {i} (id={gid}): {d}_open {o!r} is not HH:MM")
            if not TIME_RE.match(c):
                errors.append(f"row {i} (id={gid}): {d}_close {c!r} is not HH:MM")
            days.append({"open": o, "close": c})

        status = clean(raw.get("hours_status")) or None
        if status is not None and status not in STATUS_VALUES:
            errors.append(
                f"row {i} (id={gid}): hours_status {status!r} not in "
                f"{sorted(STATUS_VALUES)}"
            )
        confidence = clean(raw.get("hours_confidence")) or None
        if confidence is not None and confidence not in CONFIDENCE_VALUES:
            errors.append(
                f"row {i} (id={gid}): hours_confidence {confidence!r} not in "
                f"{sorted(CONFIDENCE_VALUES)}"
            )

        hours.append({
            "id": gid,
            "gym_name": clean(raw.get("gym_name")) or None,
            "days": days,
            "hours_source": clean(raw.get("hours_source")) or None,
            "hours_status": status,
            "hours_confidence": confidence,
            "verified_date": clean(raw.get("verified_date")) or None,
            "notes": clean(raw.get("notes")) or None,
        })

    for w in warnings:
        print(f"  warning: {w}", file=sys.stderr)

    if errors:
        print(f"Validation failed with {len(errors)} error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1

    hours.sort(key=lambda h: h["id"])

    payload = {
        "version": SCHEMA_VERSION,
        "count": len(hours),
        "hours": hours,
    }

    OUT.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(hours)} hours rows to {OUT.name}"
          f" ({len(warnings)} orphan warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
