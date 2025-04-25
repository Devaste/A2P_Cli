from cli.args import parse_cli_args
from logic.convert import convert_avif_to_png, get_real_bit_count
from logic.logging_config import configure_logging
from pathlib import Path
from PIL import Image
import sys

def run():
    args = parse_cli_args()
    if args is None:
        print("[Error] No CLI arguments provided.")
        sys.exit(1)
    configure_logging(args.log)
    if getattr(args, 'version', False):
        from logic.update_check import get_local_version
        print(f"A2P_Cli version: {get_local_version()}")
        return
    if getattr(args, 'check_update', False):
        from logic.update_check import get_local_version, get_latest_version
        local = get_local_version()
        latest = get_latest_version()
        if latest == local:
            print(f"You are running the latest version: {local}.")
        else:
            print(f"Update available: {latest} (You have {local})")
        return
    input_path = Path(args.input_dir)
    if input_path.is_file() and getattr(args, 'chk_bit', False):
        try:
            with Image.open(input_path) as img:
                n_colors, bit_count = get_real_bit_count(img)
                print(f"[CHK_BIT] {input_path.name}: {n_colors} colors, ~{bit_count} bits")
        except Exception as e:
            print(f"Error reading {input_path}: {e}")
        sys.exit(0)
    convert_avif_to_png(
        args.input_dir,
        output_dir=args.output_dir,
        replace=args.replace,
        recursive=args.recursive,
        silent=args.silent,
        qb_color=args.qb_color,
        qb_gray_color=args.qb_gray_color,
        qb_gray=args.qb_gray,
        method=args.method,
        dither=args.dither,
        log_level=args.log,
        chk_bit=args.chk_bit
    )
