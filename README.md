# A2P_Cli

**Convert AVIF images to PNG via command line.**

## Features
- Batch convert `.avif` images to `.png`.
- Greyscale images are quantized to 16 levels by default.
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

## Quantization and PIL Limitations

- The `--qb_color`, `--qb_gray-color`, and `--qb_gray` flags control the bitness of quantization for color, grayscale+one, and grayscale images, respectively.
- **Valid range:** 1–8 bits. If a value outside this range is provided, the conversion will fail for that image.
- If no quantization flag is provided:
  - Grayscale images default to 4 bits (16 levels).
  - Color images are saved without quantization.
- This limitation is due to the [Pillow (PIL) quantize() API](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize), which only supports 1–8 bits per channel for PNG output.

## Versioning

Releases follow semantic versioning: `vX.Y` for stable, `vX.Y-beta` for pre-releases. The current version is tracked in the `VERSION` file.

## Changelog
See the [GitHub Releases](https://github.com/Devaste/A2P_Cli/releases) page or the [commit log](https://github.com/Devaste/A2P_Cli/commits/main) for details.

## License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

See [LICENSE](https://www.gnu.org/licenses/agpl-3.0.html) for details.

## Contributors

- Tester: JNANEU
