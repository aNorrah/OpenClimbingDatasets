# Open Climbing Center Dataset

An open, community-maintained dataset of indoor climbing and bouldering centers around the world.

The goal of this project is to provide a freely reusable, structured dataset containing factual information about climbing centers, including:

* Climbing center names
* Chain/operator (brand)
* Street addresses
* City, region, country, and continent
* Official homepage URLs
* Official Instagram handles
* GPS coordinates
* Available climbing disciplines and training boards
* The date each record was last verified against a primary source
* Lifecycle status (open / closed) with a link to a relocated center's current record
* Whether the public can walk in and buy a day pass (chain-gym equivalence), with the day-pass price and a source

## Dataset Format

The primary dataset is stored as a single CSV file:

```text
climbing_centers.csv
```

Current schema:

| Column           | Description                                                |
| ---------------- | ---------------------------------------------------------- |
| `id`             | Stable unique identifier for the climbing center.          |
| `brand`          | Operating company or chain (e.g. Boulders, Beta Boulders). |
| `gym_name`       | Name of the physical climbing center.                      |
| `street_address` | Street address.                                            |
| `postal_code`    | Postal code.                                               |
| `city`           | City or municipality.                                      |
| `region`         | Region, state, or province (optional).                     |
| `country`        | Country name.                                              |
| `homepage`       | Official website of the center or chain.                   |
| `instagram`      | Official Instagram handle, including the leading `@` (optional). |
| `latitude`       | Latitude in decimal degrees (optional).                    |
| `longitude`      | Longitude in decimal degrees (optional).                   |
| `bouldering`     | `true` if bouldering is available.                         |
| `lead`           | `true` if lead climbing is available.                      |
| `top_rope`       | `true` if top rope climbing is available.                  |
| `moonboard`      | `true` if a MoonBoard is available.                        |
| `kilterboard`    | `true` if a Kilter Board is available.                     |
| `spraywall`      | `true` if a spray wall is available.                       |
| `continent`      | Continent name.                                            |
| `grading_type`   | Grading system the center uses. One of `color`, `font`, `v`, `none`. Blank = not yet recorded. |
| `last_verified`  | Date (`YYYY-MM-DD`) the record was last checked against a primary source. Blank = not yet verified. |
| `status`         | Lifecycle state. Blank = active/open. `closed` = no longer operating at this location. |
| `status_date`    | Date (`YYYY-MM-DD`) the status took effect (e.g. when the center closed). Blank while active. |
| `successor_id`   | If the center relocated, the `id` of the row holding the current info. Blank if it simply closed or never moved. |
| `facility_type`  | How the public can access the wall. One of `commercial_gym`, `club_wall`, `community_wall`, `leisure_centre_wall`, `outdoor_wall`, `training_space`. Blank = not yet assessed. See [Chain-gym equivalence](#chain-gym-equivalence). |
| `day_pass`       | Whether a member of the public can buy a day entry / drop-in. `true` / `false` = confirmed, `unverified` = assessed but not confirmable, blank = not assessed. |
| `chain_gym_equivalent` | `true` if the public can walk in and buy a day entry at a dedicated climbing facility (a nominal annual membership is allowed). Same `true` / `false` / `unverified` / blank convention as `day_pass`. |
| `day_pass_price` | Day-entry price with the currency inline (e.g. `145 DKK`, `10 EUR`, ranges like `129-149 DKK`). Blank = not recorded. |
| `source`         | URL the equivalence assessment is based on (prefer the center's official price/booking page). Blank = not assessed. |

> **Column order is part of the contract.** Consumers should read columns **by
> header name**, not by position. New columns are always **appended at the end**
> so that older readers keep working (see [Versioning](#versioning)).

## Data Guidelines

* One row represents **one physical climbing center**.
* Chains with multiple locations should have one entry per location, sharing the same `brand`.
* Unknown values should be left blank rather than using `N/A` or `null`.
* Boolean fields should use lowercase `true` or `false`.
* The CSV file should be encoded as UTF-8 to preserve local characters.
* Latitude and longitude should use standard WGS84 decimal coordinates.
* `instagram` stores the handle (e.g. `@boulderwelt`), not a full URL. Where a
  chain runs a single shared account, that handle is used on each of its
  locations; where a location has its own account, the per-location handle is
  used.
* `last_verified` records when a row's facts were last confirmed. **Prefer the
  center's own official website** as the source; other reliable public sources
  are acceptable when an official site is unavailable. Leave blank if the record
  has not been verified.
* `day_pass` and `chain_gym_equivalent` are **tri-state, not plain booleans**: in
  addition to `true` / `false` they may be `unverified` (assessed but day entry
  could not be confirmed — do not guess), or blank (not assessed). `day_pass_price`
  keeps the currency inline (e.g. `10 EUR`), and always set `source` when you
  assess a center. See [Chain-gym equivalence](#chain-gym-equivalence).

## `grading_type` values

- `color` — difficulty is encoded in hold colour; no numeric grade is given
  (e.g. Boulders).
- `font`  — Fontainebleau scale (6A, 6B+, 7A ...).
- `v`     — V-scale (V0, V4, V7 ...).
- `none`  — the center has no grading system; problems are ungraded.
- *(blank)* — not yet recorded. Distinct from `none`. Leave blank rather than
  guessing.

Values are lowercase and fixed. Do not introduce other values; if a center
does not fit, use `none` and add a note in the pull request.

## Lifecycle: closures and moves

Centers close and relocate. The dataset records this instead of deleting rows, so
that historical coordinates and addresses stay meaningful (a geocode that was
correct at one time still points somewhere; the live info is found via the link).

Two rules:

1. **IDs are permanent and opaque.** Never rewrite a row's location when a center
   moves, and never encode the street address in the `id` (addresses move, ids
   should not). The `id` identifies a record, not a place forever.
2. **Append, don't overwrite, on change.** Record the change in `status` /
   `status_date` / `successor_id` rather than editing the facts away.

How each case is recorded:

- **Open & current:** `status` blank, `status_date` blank, `successor_id` blank.
- **Closed for good:** keep the row, set `status = closed` and `status_date` to the
  closing date. `successor_id` stays blank. Consumers filtering for live centers
  skip `status = closed`; anyone studying history still sees it existed, with its
  last-known address and coordinates intact.
- **Relocated:** mark the old row `status = closed`, `status_date` = the move date,
  and `successor_id` = the `id` of a **new** row that carries the new address and
  coordinates (and `status` blank). Disambiguate the new id with a suffix, e.g.
  `nl-sterk-utrecht` -> `nl-sterk-utrecht-2` (or an opening-year tag). The old
  row's geocode is thereby pinned to "valid until `status_date`."

`last_verified` complements this: even with no status change, a row that is still
`active` but whose `last_verified` is old reads as "last known good" — a stale
geocode dates itself.

## Chain-gym equivalence

Not every wall in the dataset is a gym you can simply show up to and pay for. The
`facility_type`, `day_pass`, `chain_gym_equivalent`, `day_pass_price` and `source`
columns capture one externally checkable question:

> **Can a member of the public walk in and buy a day entry (drop-in / *ingresso
> giornaliero* / *dagsbillet*) during regular staffed hours, at a dedicated climbing
> facility?**

If yes, `chain_gym_equivalent = true`. A cheap **annual membership** that anyone can
buy on the spot (common in Italy, where most gyms are legally an ASD/SSD) does **not**
disqualify a center. What fails the test: members-only clubs, course-only
associations, walls inside private sports *circoli*, parish or municipal multi-sport
centres, alpine-club (CAI / DAV-style) walls, and self-managed community walls.

**`facility_type` values** (lowercase, fixed):

- `commercial_gym` — public, walk-in, day-pass climbing gym (the chain-gym equivalent).
- `club_wall` — members / association access; course- or membership-gated.
- `community_wall` — self-managed or social space.
- `leisure_centre_wall` — climbing inside a multi-sport or municipal centre.
- `outdoor_wall` — open-air public structure.
- `training_space` — small board / training room, not a general-access gym.
- *(blank)* — not yet assessed.

**Tri-state, not boolean.** `day_pass` and `chain_gym_equivalent` are `true` / `false`
when confirmed, `unverified` when a center was assessed but day entry could not be
confirmed from available sources (deliberately **not guessed**), and blank when the
center has not been assessed at all. This differs from the discipline booleans
(`bouldering` etc.), which are only `true` / `false` / blank.

**`day_pass_price`** stores the drop-in price with its currency inline (`145 DKK`,
`10 EUR`; ranges like `129-149 DKK` are fine). **`source`** is the URL the assessment
rests on — prefer the center's own price or booking page.

This layer is an **analytic classification**, not a raw fact like an address, so every
assessment should cite a `source`. Coverage is partial and grows region by region.

## Versioning

Releases are tracked in [`CHANGELOG.md`](CHANGELOG.md) and tagged in git using
[semantic versioning](https://semver.org/):

- **MAJOR** — a breaking schema change: renaming, removing, or reordering a
  column, or changing the meaning of an existing one. Consumers may need to
  update.
- **MINOR** — backward-compatible additions: a new column (always appended at
  the end) or a batch of new rows.
- **PATCH** — data corrections and small fixes that don't change the schema.

Because new columns are only ever appended and consumers read by header name,
adding a field is a MINOR change and will not break existing integrations.

## Generated file

`climbing_centers.json` is generated automatically from `climbing_centers.csv`
by a GitHub Action on every push to `main`. Do not edit the JSON by hand; edit
the CSV and let the workflow rebuild it. Apps should consume:

```
https://raw.githubusercontent.com/aNorrah/OpenClimbingDatasets/main/climbing_centers.json
```

## Contributing

Contributions are welcome! You can help by:

* Adding missing climbing centers.
* Updating addresses, homepages, or Instagram handles.
* Adding GPS coordinates.
* Correcting facility information (lead, bouldering, MoonBoard, etc.).
* Refreshing `last_verified` after re-checking a center against its official site.
* Assessing chain-gym equivalence (`facility_type`, `day_pass`,
  `chain_gym_equivalent`, `day_pass_price`) and citing a `source`.
* Expanding coverage to additional countries and continents.

Please verify information against official gym websites or other reliable public
sources whenever possible, and set `last_verified` to the date you checked.

## License

**Dataset:** CC0 1.0 Universal (Public Domain Dedication).

The dataset contains factual information intended to be freely reused by the climbing community for apps, research, maps, and other projects. Attribution is appreciated but not required.
