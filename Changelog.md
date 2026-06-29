# Changelog

All notable changes to this dataset are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/). See the
[Versioning](README.md#versioning) section of the README for what MAJOR / MINOR /
PATCH mean for this dataset.

## [1.2.0] - 2026-06-29

### Summary
- Grew to **313 climbing centers** across **24 countries** (still all Europe).
  Added **11 countries**: Croatia, Estonia, Greece, Hungary, Latvia, Lithuania,
  Poland, Portugal, Slovenia, Switzerland, United Kingdom. 230 now carry an
  Instagram handle; 260 carry latitude/longitude; 287 have a `last_verified` date.
- Introduced a **chain-gym-equivalence layer** (5 new columns): a repeatable,
  externally checkable test for whether a center is a walk-in commercial gym.
  23 centers assessed so far (all 16 in Denmark, 7 in Rome).

### Added
- `facility_type`, `day_pass`, `chain_gym_equivalent`, `day_pass_price`, `source`
  columns — the chain-gym-equivalence layer. Appended at the end. The test:
  *the public can walk in and buy a day entry (ingresso giornaliero / dagsbillet)
  during regular staffed hours at a dedicated climbing facility* — a nominal annual
  ASD/SSD membership is allowed; clubs, course-only ASDs, circolo/parish/municipal
  and community walls fail. Value convention: blank = not assessed, `unverified` =
  assessed but day entry not confirmable (not guessed), `true`/`false` = confirmed.
  Prices kept inline with currency (e.g. `145 DKK`, `10 EUR`).
  Populated for **23 centers**: **Denmark 16/16** (all `commercial_gym`, day-pass)
  and **Rome 7** (5 `commercial_gym`, 2 `club_wall`) — 19 equivalent, 2 not, 2
  unverified.
- **~125 additional centers**, expanding well beyond the original chains:
  United Kingdom (The Climbing Hangar, Depot Climbing, City Bouldering, Parthian,
  Flashpoint, Awesome Walls), a large Italy expansion (Rome, Milan, Florence,
  Turin, Bologna, Trentino, Sicily, Sardinia and many independents), Switzerland
  (Minimum, Boulderlounge, Bimano), Portugal (Vertigo, Escala25), Hungary (Spot,
  Flow, Boulder Academy), Greece, Poland (Murall, Forteca), and the Baltics /
  Balkans (Kivi, Ronimisministeerium, Falkors, Bonobo, The Hive).
- Latitude/longitude for **260** centers (up from 87) and Instagram handles for
  **230** (up from 147), continuing the geocode-first verification pass.

### Changed
- Schema is now 29 columns: the 24 core/lifecycle columns plus the 5
  equivalence columns above.

### Notes
- The equivalence columns extend **beyond the published CC0 schema** in the README.
  Update the README schema table and document the `blank` / `unverified` /
  `true`-`false` convention before tagging the release.
- `chain_gym_equivalent` is an **analytic classification** (graded by confidence in
  the working notes), not a raw factual field like the rest of the dataset. Denmark
  rows are high-confidence (official price pages); Rome rows are medium (secondary
  sources / ASD model). Detail is in `MERGE_NOTES.md`.
- Rome's **Rock Dreams** was identified as the rebranded **Rock&Walls / Lanciani
  Climbing** (same Club Lanciani venue); the equivalence is recorded on the existing
  `it-rockdreams-roma` row. One ID/address near-miss remains open
  (`it-rambla-roma` ↔ `it-rambla-vertical-roma`).
- `status` / `status_date` / `successor_id` remain unused (0 closures recorded).
- Coverage is still Europe-only and weighted toward multi-location chains; it is
  **not** an exhaustive list of every center.

### Attribution
- Coordinates derived from OpenStreetMap (c) OpenStreetMap contributors, ODbL.

## [1.1.0] - 2026-06-14

### Summary
- Grew to **188 climbing centers** across **13 countries** (added Norway; expanded
  France, Germany, Netherlands, Sweden). 147 have an Instagram handle; 87 now carry
  latitude/longitude.

### Added
- `status`, `status_date`, `successor_id` columns — a lifecycle scheme so closures
  and relocations are recorded rather than deleted. Blank `status` = active. See the
  README "Lifecycle" section and the immutable-id rule. Appended at the end.
- Latitude/longitude for 87 centers, plus street addresses, via an OpenStreetMap
  Nominatim geocoding pass (`address_checker.py --apply`).
- ~80 additional centers, search-sourced and confirmed from official homepages /
  Instagram, including chains: Klättercentret, Klätterlabbet, Klatreverket, Oslo
  Klatresenter, Altissimo, MRoc, Bloc Session, Studio Bloc, Neoliet, and many
  independents.

### Changed
- Geocoder reworked to be **geocode-first** (per-location, also yields coordinates);
  homepage scraping demoted to an opt-in fallback because chains share one homepage
  and its embedded address is the brand HQ, wrong for individual locations.
- Fixed Boulderhal Sterk (was wrongly in Amsterdam; it is in Utrecht).
- Recorded the true municipality for branded-suburb locations (e.g. boulderbar Linz
  -> Leonding).

### Removed
- Merged a Studio Bloc duplicate (one physical gym in Pfungstadt, two rows).

### Attribution
- Coordinates derived from OpenStreetMap (c) OpenStreetMap contributors, ODbL.

## [1.0.0] - 2026-06-13

First tagged release of the Open Climbing Center Dataset.

### Summary
- **105 climbing centers** across **12 countries** (Austria, Belgium, Czech
  Republic, Denmark, Finland, France, Germany, Ireland, Italy, Netherlands,
  Spain, Sweden), all in Europe.
- **85** records have an Instagram handle; **103** have a `last_verified` date.

### Added
- `instagram` column — official Instagram handle for each center (per-location
  where a center runs its own account, otherwise the shared chain handle).
  Appended after `homepage`.
- `last_verified` column — date each record was last checked against a primary
  source. Appended as the final column.
- Major European bouldering chains, one row per location, including Boulders,
  Beta Boulders, Bison Boulders (Denmark); Boulderwelt, Stuntwerk, einstein,
  Kletterfabrik (Germany); boulderbar (Austria); Arkose, Vertical'Art, Climb Up,
  Block'Out (France); Monk, Beest, Sterk, Mountain Network (Netherlands); Bleau,
  Klimzaal Blok (Belgium); Sharma Climbing, Sputnik Climbing, Indoorwall (Spain);
  Rockspot, B-Side (Italy); Klätterverket (Sweden); Boulderkeskus (Finland);
  SmíchOFF (Czech Republic); Gravity (Ireland).
- Independent Danish centers verified from their own websites: Aalborg
  Klatreklub, Nørrebro Klatreklub, OBK – Odense Boulderklub.
- `README.md` documenting the full 21-column schema, data guidelines,
  `grading_type` values, and the versioning policy.
- This `CHANGELOG.md`.

### Verified
- All 11 Boulders locations confirmed (existence, address, and per-location
  Instagram handles) against the official `boulders.dk` site and Boulders
  Linktree.
- All non-Denmark chain rows researched and dated `2026-06-13`.

### Notes
- Coverage is currently weighted toward major multi-location chains in Western
  and Northern Europe; it is **not** an exhaustive list of every center.
- A small number of records (e.g. Nørrebro Klatreklub, OBK – Odense Boulderklub)
  are listed with homepage and name only and have a blank `last_verified`,
  because their official sites are JavaScript-rendered and could not yet be read
  by a plain fetcher. These are flagged for follow-up verification.

[1.2.0]: https://github.com/aNorrah/OpenClimbingDatasets/releases/tag/v1.2.0
[1.1.0]: https://github.com/aNorrah/OpenClimbingDatasets/releases/tag/v1.1.0
[1.0.0]: https://github.com/aNorrah/OpenClimbingDatasets/releases/tag/v1.0.0
