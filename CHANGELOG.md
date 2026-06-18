# Changelog

All notable changes are documented here, following
[Keep a Changelog](https://keepachangelog.com/) and [SemVer](https://semver.org/).

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
