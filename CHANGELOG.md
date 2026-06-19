# Changelog

All notable changes are documented here, following
[Keep a Changelog](https://keepachangelog.com/) and [SemVer](https://semver.org/).

## [0.3.0]

### Added
- **`map`** (high) — `map` runs a whole subsearch per input row (capped by `maxsearches`),
  very slow and often silently truncating; redesign with `stats`/`lookup`.
- **`delete`** (high) — `delete` marks events unsearchable and is effectively irreversible;
  it should never appear in a saved or scheduled search.
- **`eventstats`** (medium) — keeps every event in memory while aggregating; prefer `stats`
  on large result sets.
- **`streamstats-unbounded`** (low) — `streamstats` with no `window=`/`time_window=`
  accumulates over all prior events.
- **`table-star`** (low) — `table *` / `fields *` selects every field — a no-op.

## [0.2.0]

### Added
- Three more SPL anti-pattern rules: `append` (`append`/`appendcols` run capped
  subsearches), `dedup` (`stats latest(...) by key` is usually faster), and
  `wildcard-field` (a base-search `field=*` is a no-op filter — scoped to not
  double-fire with `index-wildcard` or leading `=*term` wildcards).

## [0.1.0]

### Added
- SPL linter (`no-index`, `index-wildcard`, `leading-wildcard`, `join`,
  `transaction`, `subsearch`, `sort-unbounded`, `mvexpand`, `stats-first`,
  `no-sourcetype`, `no-field-trim`), a pipeline-aware formatter, and a `spllint`
  CLI that splits on top-level pipes only.
