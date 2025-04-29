# A2P_Cli

**Version:** 2.5.0

A2P_Cli is a cross-platform image batch converter with a modern PyQt5 GUI and command-line interface. It supports advanced quantization, dithering, and multi-threaded image processing with a focus on usability and performance.

## Features

- **Batch conversion** of images between formats (e.g., AVIF to PNG)
- **Quantization**: grayscale, color, and custom options
- **Dithering**: toggle and method selection
- **Multi-threaded** processing for speed
- **Modern PyQt5 GUI** with:
  - Clean, native look (light/dark themes)
  - Theme switcher with custom icons (moon/sun)
  - Responsive, fixed-size layout
- **Options saved** to `options.ini` and restored on launch
- **CLI mode** for scripting and automation
- **Automatic update check** and version display

## Project Structure

```
A2P_Cli/
├── gui/
│   ├── qt_main_window.py        # Main PyQt5 GUI logic
│   ├── qt_app.py               # GUI entry point
│   └── resources/
│       ├── light-style.qss     # Light theme stylesheet
│       ├── dark-style.qss      # Dark theme stylesheet
│       ├── light-style.svg     # Moon icon for light mode
│       ├── dark-style.svg      # Sun icon for dark mode
│       └── ...
├── logic/
│   └── convert.py              # Image conversion logic
├── cli/
│   ├── args.py                 # CLI argument parsing & help
│   ├── config.py               # CLI config helpers
│   ├── script_mode.py          # CLI/script logic
│   └── ...
├── main.py                     # Main entry point (CLI/GUI)
├── options.ini                 # Saved user options
├── requirements.txt            # Python dependencies
├── README.md
├── CHANGELOG.md
└── ...
```

## Usage

- **GUI:**
  ```sh
  python main.py
  ```
- **CLI:**
  ```sh
  python main.py [OPTIONS]
  ```

### CLI Options

```
usage: main.py [-h] [--input INPUT] [--output OUTPUT] [--remove] [--recursive]
              [--qb_gray N] [--qb_gray_color N] [--qb_color N]
              [--method {0,1,2}] [--dither {0,1}] [--max_workers N]
              [--theme {light,dark}] [--version] [--check-update]

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         Input directory
  --output OUTPUT       Output directory
  --remove              Remove originals after conversion
  --recursive           Process directories recursively
  --qb_gray N           Gray quantization level
  --qb_gray_color N     Gray+1 quantization level
  --qb_color N          Color quantization level
  --method {0,1,2}      Quantization method: 0=Median Cut, 1=Max Coverage, 2=Fast Octree
  --dither {0,1}        Dither: 0=None, 1=Floyd-Steinberg
  --max_workers N       Number of worker threads
  --theme {light,dark}  Preferred theme (GUI only)
  --version             Show version
  --check-update        Check for updates
```

## Configuration

- All settings are saved in `options.ini` (created/updated automatically).
- Theme preference (light/dark) is saved and restored.

## License

MIT License

## Credits

- Powered by PyQt5 and Pillow.
- Custom theme and icons: Devaste.
- Tester: JNANEU
