# A2P_Cli

**Convert AVIF images to PNG via command line.**

## Features
- Batch convert `.avif` images to `.png`.
- Greyscale images are quantized to 16 levels (GUI-style logic).
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
A2P_Cli.exe input_dir [--output_dir OUTPUT_DIR] [--replace] [--recursive] [--silent]
```
- `input_dir`: Directory containing `.avif` files (required)
- `--output_dir`: Output directory for `.png` files (optional)
- `--replace`: Remove original `.avif` files after conversion (flag)
- `--recursive`: Search for `.avif` files recursively (flag)
- `--silent`: Suppress per-file output, only print summary (flag)

### Python Script
Run with Python (for development or advanced use):

```
python main.py input_dir [--output_dir OUTPUT_DIR] [--replace] [--recursive] [--silent]
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
