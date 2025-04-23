# A2P_Cli - AVIF to PNG Converter

**This is the main public release (v1.5, stable).**

A modular, robust CLI tool for converting AVIF images to PNG with advanced quantization and dithering options.

## Features
- **Interactive CLI** with menu navigation and option editing
- **Advanced options**: quantization method, dither, per-mode bit depth
- **Centralized config** for defaults, descriptions, and validation
- **Type-checked, modular codebase** for maintainability
- **Automated tests** for all validators and menu helpers
- Convert AVIF to PNG (lossless or quantized)
- Quantize PNGs with custom bit-depth (color/gray)
- Batch and recursive folder conversion
- Output to custom directory
- Remove originals after conversion (`--replace`)
- Logging and silent mode
- **NEW:** `--chk_bit` shows real color count/bit-depth for single or all output images

## Project Structure
```
A2P_Cli/
├── cli/
│   ├── menu.py           # Main menu logic
│   ├── config.py         # All defaults, descriptions, and validators
│   ├── menu_helpers.py   # Menu rendering/input helpers
├── logic/
│   ├── convert.py        # Conversion logic
│   ├── update_check.py   # Update/version check logic
├── main.py               # Entry point
├── README.md
├── CHANGELOG.md
...
```

## CLI Options
- **input_dir**: Directory containing .avif files (required)
- **--output_dir OUTPUT_DIR**: Directory to save .png files (default: same as input_dir)
- **--replace**: Remove original .avif files after conversion
- **--recursive**: Recursively search for .avif files in subdirectories
- **--silent**: No output to command line, only finishing result
- **--qb_color N**: Quantization bitness for color images (1–8, i.e., 2–256 colors)
- **--qb_gray-color N**: Quantization bitness for grayscale+one images (1–8, i.e., 2–256 levels)
- **--qb_gray N**: Quantization bitness for grayscale images (1–8, i.e., 2–256 levels)
- **--method N**: Quantization method. Options:
    - 0: Median Cut (slower, high quality)
    - 1: Maximum Coverage (alternative, slower)
    - 2: Fast Octree (default, fastest, good for most images)
- **--dither N**: Dithering method. Options:
    - 0: None (no dithering, may cause banding)
    - 1: Floyd-Steinberg (default, visually smooths gradients)
- **--chk_bit**: Print real bit-depth (unique color count) for each output
- **--version**: Print the current version and exit
- **--check-update**: Check for updates and exit

See the [Pillow quantize() documentation](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize) for more details.

### Example
```sh
python main.py --version
python main.py --check-update
python main.py input_dir --output_dir out --qb_color 4 --replace --method 2 --dither 1
python main.py myimg.avif --chk_bit
python main.py ./input --output_dir ./out --recursive --qb_color 4 --chk_bit
```

### Option Details
- **method**: Controls how the palette is chosen for quantization. '2' (Fast Octree) is fastest and works well for most images. '0' (Median Cut) and '1' (Max Coverage) may be higher quality for some images, especially with many colors.
- **dither**: Controls how color transitions are smoothed. '1' (Floyd-Steinberg) is the default and gives smoother gradients. '0' disables dithering, which may make banding more visible but sometimes gives a cleaner look for flat-color art.

## Requirements
- Python 3.7+
- Pillow >= 9.0.0
- numpy
- requests

## Test & Coverage
Run all tests:
```sh
pytest --maxfail=3 --disable-warnings -q
```

Check coverage:
```sh
pytest --cov=logic --cov=cli
```

## Developer Notes
- All default values, option descriptions, and input validation are in `cli/config.py`.
- Menu rendering and input helpers are in `cli/menu_helpers.py`.
- All CLI and helper logic is type-annotated for clarity and editor support.
- To run tests: `pytest tests/`

## Changelog
**v1.5**
- Output dir logic fixed (preserves structure)
- Quantization options restored
- `--chk_bit` for real color/bit check
- Full test pass

See [CHANGELOG.md](CHANGELOG.md) for details on the latest stable release (v1.5) and previous versions.

## License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

See [LICENSE](https://www.gnu.org/licenses/agpl-3.0.html) for details.

## Contributors

- Tester: JNANEU
