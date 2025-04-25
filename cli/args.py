from .config import DEFAULT_LOG_LEVEL
from cli.globals import cli_args
import argparse
import sys

def parse_cli_args():
    if len(sys.argv) == 1:
        return None  # Signal: launch menu
    parser = argparse.ArgumentParser(
        description="""
A2P_Cli - AVIF to PNG Converter

Converts AVIF images to PNG, with advanced quantization and batch options.
Supports both interactive TUI and script/CLI operation.

USAGE:
  a2pcli <input_dir> [--output_dir DIR] [OPTIONS...]
  a2pcli --save [other options]
  a2pcli <input_dir> --options
  a2pcli single_file.avif --chk_bit
  a2pcli --version
  a2pcli --check-update

COMMON OPTIONS:
  input_dir               Directory or file to convert (required unless --version or --check-update)
  --output_dir DIR        Directory to save .png files (default: same as input)
  --remove                Remove original .avif files after conversion
  --recursive             Recursively search for .avif files in subdirectories
  --silent                No output to command line, only finishing result
  --qb_color N            Quantization bits for color images (1–8)
  --qb_gray_color N       Quantization bits for grayscale+one images (1–8)
  --qb_gray N             Quantization bits for grayscale images (1–8)
  --method N              Quantization method: 0=Median Cut, 1=Max Coverage, 2=Fast Octree
  --dither N              Dither: 0=None, 1=Floyd-Steinberg
  --log N                 Set logging level: 0=off, 1=error, 2=warning, 3=info, 4=debug
  --chk_bit               Check and display real bit depth (unique color count) for each converted image or single file
  --save                  Save current CLI options to the [CLI] block in options.ini and exit
  --options               Load CLI options from the [CLI] block in options.ini (overrides other CLI args except input_dir)
  --version               Show version and exit
  --check-update          Check for updates and exit

EXAMPLES:
  a2pcli images/ --qb_color 4 --method 1 --dither 1
  a2pcli images/example.avif --chk_bit
  a2pcli --save --qb_color 8 --recursive
  a2pcli images2/ --options

Options can also be saved/loaded in options.ini ([CLI] section).
For TUI mode, run without arguments.
        """
    )
    parser.add_argument("input_dir", type=str, nargs="?", help="Directory or file to convert (required unless --version or --check-update)")
    parser.add_argument("--output_dir", type=str, default=None, help="Directory to save .png files (default: same as input)")
    parser.add_argument("--remove", action="store_true", help="Remove original .avif files after conversion")
    parser.add_argument("--recursive", action="store_true", help="Recursively search for .avif files in subdirectories")
    parser.add_argument("--silent", action="store_true", help="No output to command line, only finishing result")
    parser.add_argument("--qb_color", type=int, help="Quantization bits for color images (1–8)")
    parser.add_argument("--qb_gray_color", type=int, help="Quantization bits for grayscale+one images (1–8)")
    parser.add_argument("--qb_gray", type=int, help="Quantization bits for grayscale images (1–8)")
    parser.add_argument("--method", type=int, choices=[0, 1, 2], help="Quantization method: 0=Median Cut, 1=Max Coverage, 2=Fast Octree")
    parser.add_argument("--dither", type=int, choices=[0, 1], help="Dither: 0=None, 1=Floyd-Steinberg")
    parser.add_argument("--log", type=int, default=DEFAULT_LOG_LEVEL, choices=[0, 1, 2, 3, 4], help="Set logging level: 0=off, 1=error, 2=warning, 3=info, 4=debug")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("--check-update", action="store_true", help="Check for updates and exit")
    parser.add_argument("--chk_bit", action="store_true",help="Check and display real bit depth (unique color count) for each converted image or single file.")
    parser.add_argument("--save", action="store_true", help="Save current CLI options to the [CLI] block in options.ini and exit.")
    parser.add_argument("--options", action="store_true", help="Load CLI options from the [CLI] block in options.ini (overrides other CLI args except input_dir).")
    args = parser.parse_args()
    # Enforce input_dir only if not version/check-update
    if not (args.version or args.check_update) and not args.input_dir:
        parser.error("the following arguments are required: input_dir")
    cli_args.update(vars(args))
    return cli_args
