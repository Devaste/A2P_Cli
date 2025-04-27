# A2P_Cli - AVIF to PNG Converter

**Version 2.4.0 (2025-04-27)**

A modular, robust tool for converting AVIF images to PNG with advanced quantization, dithering, and both interactive TUI and scriptable CLI modes. Features centralized logging, persistent config, and a clean, maintainable codebase.

## Features
- **Interactive TUI**: Menu-driven interface for easy option editing and batch conversion
- **Script/CLI mode**: Full-featured command-line interface for automation and scripting
- **Advanced options**: Quantization methods, dithering, per-mode bit depth
- **Persistent config**: Save/load options via `options.ini` ([CLI] and [TUI] sections)
- **Centralized logging**: All actions and errors logged to `a2pcli.log` for easy debugging
- **Automated tests** for validators and helpers
- **Batch and recursive conversion**
- **Real bit-depth check**: `--chk_bit` shows color/bit info for any image
- **MAN-style help**: `-h`/`--help` shows usage, options, and examples
- **Self-updating**: Robust update mechanism for all deployment types (Windows EXE, Unix binary, Python script) with platform-aware asset selection, extraction, and relaunch. CLI prompts for update unless --silent is set (auto-updates); TUI prompts interactively.

## Project Structure
```
A2P_Cli/
├── cli/
│   ├── args.py           # Argument parsing & help
│   ├── config.py         # CLI/TUI config helpers
│   ├── globals.py        # Shared CLI globals
│   ├── options_io.py     # Config load/save
│   ├── script_mode.py    # CLI/script logic
│   ├── tui_mode.py       # TUI logic
│   ├── tui_utils.py      # TUI helper functions
│   └── __init__.py
├── logic/
│   ├── convert.py        # Conversion logic
│   ├── logging_config.py # Logging setup & decorators
│   ├── update_check.py   # Version/update check
│   └── __init__.py
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
├── VERSION               # App version
├── CHANGELOG.md          # Release notes
├── README.md             # This file
├── LICENSE
├── icon.ico
├── .gitignore
```

**Note:** Anywhere you see `python main.py`, you can also use `a2pcli` or `a2pcli.exe` if installed globally or on Windows. All CLI commands and options are identical.

## How to Run

You can use `python main.py`, `a2pcli`, or `a2pcli.exe` interchangeably for all commands below. For clarity, all examples below use `python main.py`—simply substitute your preferred command as needed.

- **TUI mode (interactive menu):**
  ```sh
  python main.py
  ```
- **CLI/script mode (batch conversion, automation):**
  ```sh
  python main.py <input_dir> [OPTIONS...]
  python main.py <input_dir> --qb_color 4 --method 1 --dither 1
  python main.py <input_dir> --options
  python main.py --version
  python main.py --check-update   # Now supports in-app update with prompt/auto-update
  ```

## CLI Options

All CLI options are summarized below. For a full, up-to-date usage guide and examples, see the [Usage & Help](#usage--help) section.

- **input_dir**: Directory or file to convert (required unless --version or --check-update)
- **--output_dir DIR**: Directory to save .png files (default: same as input)
- **--remove**: Remove original .avif files after conversion
- **--recursive**: Recursively search for .avif files in subdirectories
- **--silent**: No output to command line, only finishing result
- **--qb_color BIT_COUNT**: Quantization bits for color images (1–8, 2–256 colors)
- **--qb_gray_color BIT_COUNT**: Quantization bits for grayscale+one images (1–8, 2–256 levels)
- **--qb_gray BIT_COUNT**: Quantization bits for grayscale images (1–8, 2–256 levels)
- **--method {0,1,2}**: Quantization method: 0=Median Cut, 1=Max Coverage, 2=Fast Octree
- **--dither {0,1}**: Dither: 0=None, 1=Floyd-Steinberg
- **--chk_bit**: Check and display real bit depth for each converted image or file
- **--save**: Save current CLI options to the [CLI] block in options.ini and exit
- **--options**: Load CLI options from the [CLI] block in options.ini (overrides other CLI args except input_dir)
- **--version**: Show version and exit
- **--check-update**: Check for updates and exit

## Usage & Help

```
A2P_Cli - AVIF to PNG Converter

USAGE:
  python main.py
  python main.py input_dir [OPTIONS]
  python main.py -h | --help      Show this message
  python main.py -v | --version  Show version
  python main.py -u | --check-update  Check for updates

EXAMPLES:
  python main.py images/ --qb_color 4 --method 1
  python main.py images/example.avif --chk_bit

OPTIONS:
  --output_dir DIR         Directory to save .png files (default: same as input)
  --remove                 Remove original .avif files after conversion
  --recursive              Recursively search for .avif files in subdirectories
  --silent                 No output to command line, only finishing result
  --qb_color BIT_COUNT     Quantization bits for color images (1–8, 2–256 colors)
  --qb_gray_color BIT_COUNT Quantization bits for grayscale+one images (1–8, 2–256 levels)
  --qb_gray BIT_COUNT      Quantization bits for grayscale images (1–8, 2–256 levels)
  --method {0,1,2}        Quantization method: 0=Median Cut, 1=Max Coverage, 2=Fast Octree
  --dither {0,1}          Dither: 0=None, 1=Floyd-Steinberg
  --chk_bit               Check and display real bit depth for each converted image or file
  --save                  Save current options to options.ini [CLI block]
  --options               Load options from options.ini [CLI block]
  -v, --version           Show version and exit
  -u, --check-update      Check for updates and exit

COMMON OPTIONS can be saved/loaded in options.ini (CLI) or set in TUI.
```

## Usage Examples

```sh
# Launch TUI (interactive menu)
python main.py

# Convert a folder with quantization and dithering
python main.py images/ --qb_color 4 --method 1 --dither 1

# Convert a single file and check bit depth
python main.py image.avif --chk_bit

# Save current CLI options for reuse
python main.py images/ --qb_color 8 --recursive --save

# Use saved options, override input_dir
python main.py images2/ --options
```

## Logging
- All actions/errors are logged for easy debugging.

## Persistent Config
- Options can be saved/loaded under `[CLI]` or `[TUI]` sections.

---

For more, see `python main.py -h` or `a2pcli -h` for MAN-style help with all options and examples.

Contributors:
JNANEU - Tester
