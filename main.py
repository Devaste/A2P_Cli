import sys
from cli.args import parse_cli_args
from logic.logging_config import configure_logging
from cli.menu import run
from logic.convert import convert_single_image, convert_avif_to_png, get_real_bit_count
from pathlib import Path
from PIL import Image

def main():
    args = parse_cli_args()
    if args is None:
        run()
        sys.exit(0)
    configure_logging(args.log)

    # Early exit for --version and --check-update
    if getattr(args, 'version', False) or getattr(args, 'check_update', False):
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

    if getattr(args, 'chk_bit', False):
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
            chk_bit=args.chk_bit,
        )
    else:
        run(args=args)

if __name__ == "__main__":
    main()
