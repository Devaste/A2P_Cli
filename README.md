# A2P_Cli

**Version:** 3.0.0 – Final Release

A2P_Cli is a fast, cross-platform batch image converter with a modern PyQt5 GUI and CLI. It supports AVIF to PNG conversion, advanced quantization and dithering, and multi-threaded processing. Designed for usability, performance, and maintainability.

---

## Features

- **Batch convert** AVIF images to PNG
- **Quantization**: Color, grayscale, and grayscale+one with custom bit depth
- **Dithering**: Toggle and select method
- **Multi-threaded** for high performance
- **Modern GUI**:
  - PyQt5, native look, light/dark themes
  - Theme switcher with custom icons
  - Fixed, responsive layout
- **Options saved** to `options.ini` and auto-restored
- **CLI mode** for automation and scripting
- **Cross-platform**: Windows, macOS, Linux

---

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/A2P_Cli.git
   cd A2P_Cli
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

---

## Usage

### GUI
Launch the graphical interface:
```sh
python main.py
```

### CLI
Run batch conversions via command line:
```sh
python main.py --input_dir <input> [--output_dir <output>] [options]
```

#### Common CLI Options
- `--input_dir`   Directory containing .avif files (required)
- `--output_dir`  Directory for output .png files (default: input)
- `--remove`      Remove original .avif files after conversion
- `--recursive`   Recursively search subdirectories
- `--silent`      Minimal output
- `--qb_color`    Quantization bits for color images (1–8)
- `--qb_gray_color` Quantization bits for grayscale+one
- `--qb_gray`     Quantization bits for grayscale
- `--method`      Quantization method (0=Median Cut, 1=Max Coverage, 2=Fast Octree)
- `--dither`      Dither (0=None, 1=Floyd-Steinberg)
- `--max_workers` Number of parallel workers

---

## Project Structure

```
A2P_Cli/
├── gui/
│   ├── qt_main_window.py        # Main PyQt5 GUI logic
│   ├── qt_app.py               # GUI entry point
│   └── resources/              # Themes & icons
├── logic/
│   ├── convert.py              # Image conversion logic
│   ├── config.py, ...
├── cli/
│   ├── args.py, ...            # CLI helpers
├── main.py                     # Main entry point
├── options.ini                 # Saved user options
├── requirements.txt            # Python dependencies
├── README.md
└── ...
```

---

## Best Practices & Design
- **Modular codebase**: GUI, logic, and CLI are separated
- **No deprecated code or unused imports**
- **Docstrings** and comments throughout
- **Extensible**: Easy to add new formats or features

---

## License
MIT License – see [LICENSE](LICENSE)

---

## Acknowledgements
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/intro/)
- [Pillow](https://python-pillow.org/)
- AVIF plugin: [pillow-avif-plugin](https://github.com/helixy2k/pillow-avif-plugin)
- **Special thanks to [JNANEU](https://github.com/JNANEU) for the initial project idea and extensive testing**

---

## Final Notes
This is the final, stable release (3.0.0). For questions or contributions, open an issue or pull request on GitHub.
