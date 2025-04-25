# A2P_Cli - AVIF to PNG Converter

**Version 2.0 (stable, 2025)**

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

## Project Structure
```
A2P_Cli/
├── cli/
│   ├── tui_mode.py       # TUI logic
│   ├── script_mode.py    # CLI/script logic
│   ├── args.py           # Argument parsing & MAN-style help
│   ├── options_io.py     # Config load/save
├── logic/
│   ├── convert.py        # Conversion logic
│   ├── logging_config.py # Logging setup & decorators
│   ├── update_check.py   # Version/update check
├── main.py               # Entry point
├── README.md
...
```

## How to Run
- **TUI mode:**
  ```sh
  python main.py
  # or
  a2pcli
  ```
- **CLI/script mode:**
  ```sh
  python main.py <input_dir> [OPTIONS...]
  a2pcli <input_dir> --qb_color 4 --method 1 --dither 1
  a2pcli <input_dir> --options
  a2pcli --version
  a2pcli --check-update
  ```

## CLI Options
- **input_dir**: Directory or file to convert (required unless --version or --check-update)
- **--output_dir DIR**: Directory to save .png files (default: same as input)
- **--remove**: Remove original .avif files after conversion
- **--recursive**: Recursively search for .avif files in subdirectories
- **--silent**: No output to command line, only finishing result
- **--qb_color N**: Quantization bits for color images (1–8)
- **--qb_gray_color N**: Quantization bits for grayscale+one images (1–8)
- **--qb_gray N**: Quantization bits for grayscale images (1–8)
- **--method N**: Quantization method: 0=Median Cut, 1=Max Coverage, 2=Fast Octree
- **--dither N**: Dither: 0=None, 1=Floyd-Steinberg
- **--log N**: Set logging level: 0=off, 1=error, 2=warning, 3=info, 4=debug
- **--chk_bit**: Check and display real bit depth (unique color count) for each converted image or single file
- **--save**: Save current CLI options to the [CLI] block in options.ini and exit
- **--options**: Load CLI options from the [CLI] block in options.ini (overrides other CLI args except input_dir)
- **--version**: Show version and exit
- **--check-update**: Check for updates and exit

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

# Check version or updates
python main.py --version
python main.py --check-update
```

## Logging
- All actions/errors are logged for easy debugging.

## Persistent Config
- Options can be saved/loaded under `[CLI]` or `[TUI]` sections.

---

For more, see `python main.py -h` or `a2pcli -h` for MAN-style help with all options and examples.

Contributors:
JNANEU - Tester
