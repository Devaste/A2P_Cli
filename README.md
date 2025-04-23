# A2P_Cli - AVIF to PNG Converter (2.0-beta)

A modular, robust CLI tool for converting AVIF images to PNG with advanced quantization and dithering options.

## Features
- **Interactive CLI** with menu navigation and option editing
- **Advanced options**: quantization method, dither, per-mode bit depth
- **Centralized config** for defaults, descriptions, and validation
- **Type-checked, modular codebase** for maintainability
- **Automated tests** for all validators and menu helpers

## Project Structure
```
A2P_Cli/
├── cli/
│   ├── menu.py           # Main menu logic
│   ├── config.py         # All defaults, descriptions, and validators
│   ├── menu_helpers.py   # Menu rendering/input helpers
│   └── __init__.py
├── logic/
│   ├── convert.py        # Conversion logic
│   └── __init__.py
├── tests/
│   ├── test_validators.py
│   ├── test_menu_helpers.py
│   └── __init__.py
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
- **--version**: Print the current version and exit
- **--check-update**: Check for updates and exit

See the [Pillow quantize() documentation](https://pillow.readthedocs.io/en/stable/reference/Image.html#PIL.Image.Image.quantize) for more details.

### Example
```sh
python main.py --version
python main.py --check-update
python main.py input_dir --output_dir out --qb_color 4 --replace --method 2 --dither 1
```

### Option Details
- **method**: Controls how the palette is chosen for quantization. '2' (Fast Octree) is fastest and works well for most images. '0' (Median Cut) and '1' (Max Coverage) may be higher quality for some images, especially with many colors.
- **dither**: Controls how color transitions are smoothed. '1' (Floyd-Steinberg) is the default and gives smoother gradients. '0' disables dithering, which may make banding more visible but sometimes gives a cleaner look for flat-color art.

## Developer Notes
- All default values, option descriptions, and input validation are in `cli/config.py`.
- Menu rendering and input helpers are in `cli/menu_helpers.py`.
- All CLI and helper logic is type-annotated for clarity and editor support.
- To run tests: `pytest tests/`

## Changelog
See [CHANGELOG.md](CHANGELOG.md) for details on the 2.0-beta release and previous versions.

## License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

See [LICENSE](https://www.gnu.org/licenses/agpl-3.0.html) for details.

## Contributors

- Tester: JNANEU
