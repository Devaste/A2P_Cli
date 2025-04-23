# A2P_Cli

**Convert AVIF images to PNG via command line.**

## Features
- Batch convert `.avif` images to `.png`.
- Greyscale images are quantized to 16 levels (GUI-style logic) by default.
- Optional quantization bitness for color, grayscale+one, and grayscale images via `--qb_color`, `--qb_gray-color`, and `--qb_gray` flags.
- Supports recursive conversion in subfolders.
- Optionally deletes original `.avif` files after conversion.
- Customizable output directory.
- Silent mode for scripting.

## Installation
Install the required dependencies with pip (works in PowerShell, CMD, or Bash):

```sh
pip install -r requirements.txt
```

## Usage

### Windows Executable
After downloading the release (`A2P_Cli.exe`), run from command prompt:

```
A2P_Cli.exe input_dir [--output_dir OUTPUT_DIR] [--replace] [--recursive] [--silent] [--qb_color QB_COLOR] [--qb_gray-color QB_GRAY_COLOR] [--qb_gray QB_GRAY]
```
- `input_dir`: Directory containing `.avif` files (required)
- `--output_dir`: Output directory for `.png` files (optional)
- `--replace`: Remove original `.avif` files after conversion (flag)
- `--recursive`: Search for `.avif` files recursively (flag)
- `--silent`: Suppress per-file output, only print summary (flag)
- `--qb_color QB_COLOR`: Quantization bitness for color images (optional)
- `--qb_gray-color QB_GRAY_COLOR`: Quantization bitness for grayscale+one images (optional)
- `--qb_gray QB_GRAY`: Quantization bitness for grayscale images (optional)

### Python Script
Run with Python (for development or advanced use):

```
python main.py input_dir [--output_dir OUTPUT_DIR] [--replace] [--recursive] [--silent] [--qb_color QB_COLOR] [--qb_gray-color QB_GRAY_COLOR] [--qb_gray QB_GRAY]
```

## Versioning

Releases follow semantic versioning: `vX.Y` for stable, `vX.Y-beta` for pre-releases. The current version is tracked in the `VERSION` file.

## Changelog
See the [GitHub Releases](https://github.com/Devaste/A2P_Cli/releases) page or the [commit log](https://github.com/Devaste/A2P_Cli/commits/main) for details.

## License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

See [LICENSE](https://www.gnu.org/licenses/agpl-3.0.html) for details.

## Contributors

- Tester: JNANEU
