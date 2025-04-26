import argparse
from logic.logging_config import log_call

@log_call
def parse_cli_args():
    """
    Parse command-line arguments for the A2P_Cli tool using argparse.
    Returns:
        tuple: (mode, args_dict), where mode is one of 'meta', 'functional', or 'conversion'.
    Raises:
        SystemExit: If required arguments are missing or help/version/update is requested.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=False  # Prevent argparse from adding its own help argument
    )

    # Re-add help manually so it only appears once
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit')

    # === Mandatory ===
    parser.add_argument("input_dir", type=str, nargs="?", help="Directory or file to convert (required unless --version or --check-update)")

    # === Optional (Conversion/Operation Options) ===
    parser.add_argument("--output_dir", type=str, default=None, help="Directory to save .png files (default: same as input)")
    parser.add_argument("--remove", action="store_true", help="Remove original .avif files after conversion")
    parser.add_argument("--recursive", action="store_true", help="Recursively search for .avif files in subdirectories")
    parser.add_argument("--silent", action="store_true", help="No output to command line, only finishing result")
    parser.add_argument("--qb_color", type=int, metavar="BIT_COUNT", help="Quantization bits for color images (1–8)")
    parser.add_argument("--qb_gray_color", type=int, metavar="BIT_COUNT", help="Quantization bits for grayscale+one images (1–8)")
    parser.add_argument("--qb_gray", type=int, metavar="BIT_COUNT", help="Quantization bits for grayscale images (1–8)")
    parser.add_argument("--method", type=int, choices=[0, 1, 2], help="Quantization method: 0=Median Cut, 1=Max Coverage, 2=Fast Octree")
    parser.add_argument("--dither", type=int, choices=[0, 1], help="Dither: 0=None, 1=Floyd-Steinberg")
    parser.add_argument("--chk_bit", action="store_true", help="Check and display real bit depth for each converted image or file.")

    # === Functional Options ===
    parser.add_argument("--save", action="store_true", help="Save current CLI options to the [CLI] block in options.ini and exit.")
    parser.add_argument("--options", action="store_true", help="Load CLI options from the [CLI] block in options.ini (overrides other CLI args except input_dir).")
    parser.add_argument("-v", "--version", action="store_true", help="Show version and exit")
    parser.add_argument("-u", "--check-update", action="store_true", help="Check for updates and exit")

    args = parser.parse_args()
    args_dict = vars(args)

    # Decide mode
    if args_dict.get('version') or args_dict.get('check_update'):
        return 'meta', args_dict
    if args_dict.get('save') or args_dict.get('options'):
        return 'functional', args_dict
    if args.input_dir:
        return 'conversion', args_dict
    parser.error("the following arguments are required: input_dir")
