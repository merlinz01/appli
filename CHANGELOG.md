# Changelog

This is the changelog for Tarmac.

## [Unreleased]

### Added

- Accept `pathlib.Path` objects for `Runner.base_path`

## [0.1.8]

### Added

- Add `exists`, `isfile`, and `isdir` condition helpers
- Add `changed` condition helper
- Add `skipped` condition helper
- Add workflow step parameter value substitution

## [0.1.7]

### Added

- Allow multiple commands to be specified in a `run` workflow step
- Add `stdin` parameter to `run` workflow step
- Add `--script` argument to `tarmac` command for running scripts directly

## [0.1.6]

### Added

- Add workflow step hook to runner
- Add `python` workflow step type
- Add `--output-format` argument to command
- Add `--log-level` argument to command
- Add `--output-file` argument to command
- Add `text` output format
- Add `--version` argument to command
- Add `colored-text` as default output format
- Add `Failure` exception for use in scripts
- Add JSON schema for workflow definition files
- Add `cwd` and `env` arguments to `run` workflow step
- Add `steps` variable to Python workflow step environment

### Changed

- Cache `uv` command path in runner
- Pass `--native-tls` flag to `uv` command
- Change default output format to JSON
- Move sample scripts and workflows to git submodule
- Improve text output format
- Use `uv_build` package build backend

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
