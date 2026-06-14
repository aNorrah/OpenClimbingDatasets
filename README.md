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
* Expanding coverage to additional countries and continents.

Please verify information against official gym websites or other reliable public
sources whenever possible, and set `last_verified` to the date you checked.

## License

**Dataset:** CC0 1.0 Universal (Public Domain Dedication).

The dataset contains factual information intended to be freely reused by the climbing community for apps, research, maps, and other projects. Attribution is appreciated but not required.
