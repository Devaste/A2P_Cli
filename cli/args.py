from .config import DEFAULT_METHOD, DEFAULT_DITHER, DEFAULT_LOG_LEVEL
from cli.globals import cli_args
import argparse
import sys

def parse_cli_args():
    if len(sys.argv) == 1:
        return None  # Signal: launch menu
    parser = argparse.ArgumentParser(description="A2P_Cli: AVIF to PNG Converter")
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
    args = parser.parse_args()
    # Enforce input_dir only if not version/check-update
    if not (args.version or args.check_update) and not args.input_dir:
        parser.error("the following arguments are required: input_dir")
    cli_args.update(vars(args))
    return cli_args
