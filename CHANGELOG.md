# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0/).

## [1.2] - 2025-04-23
### Changed
- Bundled the VERSION file with the executable using PyInstaller for reliable version detection in both source and packaged modes.
- Updated workflow to ensure the VERSION file is always included in release artifacts.

## [1.1] - 2025-04-23
### Fixed
- Bundled `requests` dependency with the app to resolve missing module error in packaged builds.
- Ensured workflow-based and manual builds include all required dependencies.

## [1.0] - 2025-04-23
### Initial Release
- First public release of A2P_Cli: AVIF to PNG Converter.
- Modular CLI, robust validation, 100% test coverage, and cross-platform support.
- Features: interactive conversion, configurable options, quantization, dither, batch processing, and more.

## [2.2] - 2025-04-23
### Added
- Automatic update check on startup: notifies user if a new version is available on GitHub Releases.
- Added logic/update_check.py module for robust version comparison and notification.

### Improved
- Menu refreshes on every menu change for a cleaner CLI experience.

## [2.1] - 2025-04-23
### Improved
- CLI now clears the terminal before displaying each menu for a true "refresh" effect, improving UX.
- Added cross-platform clear_screen utility and integrated it into the options menu.
- Cleaned up unused imports and references in tests and codebase.
- Streamlined .gitignore for modern Python/pytest/coverage workflows.
- Added .gitattributes for cross-platform line ending consistency.
- Maintained 100% code coverage and robust test suite.

## [2.0-beta] - 2025-04-23
### Major Changes
- Modularized CLI: menu logic, config, and helpers split into separate files.
- Centralized all default values, option descriptions, and validators in `cli/config.py`.
- Fully type-checked and linter-compliant conversion logic.
- Robust, reusable input validation for all CLI options.
- Added `method` and `dither` options for quantization and dithering control.
- All menu and helper logic now unit tested in `tests/`.
- Improved docstrings and code documentation throughout.
- Project is now ready for further extension and easy maintenance.

### Breaking Changes
- CLI options and menu structure may differ from previous versions.
- Some internal APIs have changed for consistency and extensibility.

## [v1.2] - 2025-04-23

### Changed
- Refactored convert_single_image for lower cognitive complexity and better error handling.
- Enforced quantization bitness limits (1–8) for all qb_* flags due to PNG/PIL limitations. Added error messages and documentation links for user clarity.
- Improved CLI help text for quantization flags to document limitations and link to PIL docs.

### Fixed
- Minor code cleanup and improved maintainability.

## [v1.1-beta] - 2025-04-23

### Added
- CLI flags: `--qb_color`, `--qb_gray-color`, and `--qb_gray` for custom quantization bitness of color, grayscale+one, and grayscale images.
- Conversion logic updated to use these flags if provided.
- README updated to document new flags and usage.

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
