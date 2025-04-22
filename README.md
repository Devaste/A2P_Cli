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
Run the script with Python (use `python` or `python3` as appropriate):

```sh
python convert.py <input_dir> [--output_dir OUTPUT] [--replace] [--recursive] [--silent] [--log [LOG]]
```
- `<input_dir>`: Directory containing `.avif` files (required)
- `--output_dir`: Output directory for `.png` files (optional)
- `--replace`: Remove original `.avif` files after conversion (flag)
- `--recursive`: Search for `.avif` files recursively (flag)
- `--silent`: Suppress per-file output, only print summary (flag)
- `--log`: Enable logging to `convert.log` (optional, default log level is 20 = INFO)

## Logging

You can enable logging to `convert.log` using the `--log` flag:

    python convert.py <input_dir> --log

To set the log level, pass a number (default is 20 = INFO):

    python convert.py <input_dir> --log 10   # DEBUG
    python convert.py <input_dir> --log 20   # INFO
    python convert.py <input_dir> --log 30   # WARNING
    python convert.py <input_dir> --log 40   # ERROR
    python convert.py <input_dir> --log 50   # CRITICAL

## License
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).

See [LICENSE](https://www.gnu.org/licenses/agpl-3.0.html) for details.

## Contributors

- Tester: JNANEU
