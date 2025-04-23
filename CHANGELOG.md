# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v1.0-beta] - 2025-04-23

### Added
- Semantic versioning using a VERSION file; releases are now tagged as `vX.Y` or `vX.Y-beta`.
- Custom Windows executable icon (`icon.ico`) with a text-based gradient design.

### Changed
- CLI usage: Required argument `input_dir` now appears before optional arguments in help and error messages.
- README: Updated usage examples for both Windows executable and Python script; clarified versioning and changelog sections; removed deprecated logging flags.
- Release workflow: Now reads version from VERSION file and applies correct tag format for main and beta releases.
- Silent mode: Warnings and errors are always shown, even when `--silent` is used.

### Fixed
- Recursive conversion now saves PNGs in the correct directories.
- Fixed cognitive complexity issues in conversion logic.
