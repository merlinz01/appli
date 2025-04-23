# Changelog

This is the changelog for Tarmac.

## [Unreleased]

### Added

- Add workflow step hook to runner
- Add `python` workflow step type
- Add `--output-format` argument to command
- Add `--log-level` argument to command
- Add `--output-file` argument to command
- Add `text` output format
- Add `--version` argument to command
- Add `colored-text` as default output format

### Changed

- Cache `uv` command path in runner
- Pass `--native-tls` flag to `uv` command
- Change default output format to JSON
- Move sample scripts and workflows to git submodule
- Improve text output format

## [0.1.5]

- Unify workflow terminology

## [0.1.4]

### Changed

- Ignore missing script and workflow metadata

### Fixed

- Improve handling of corrupted outputs file

## 0.1.3

### Changed

- Add build artifacts to release assets

## 0.1.2

### Fixed

- Improve release CI workflow

## 0.1.1

### Added

- Add CI and release workflows
- Add `--base-path` argument to  `tarmac` command

## 0.1.0

Initial release.
