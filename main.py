import sys
from cli.args import parse_cli_args
from logic.update_check import check_for_update, get_local_version
from logic.logging_config import configure_logging
from cli.menu import run
from logic.convert import convert_single_image, convert_avif_to_png, get_real_bit_count
from pathlib import Path
from PIL import Image

def main():
    args = parse_cli_args()
    configure_logging(args.log)

    if args.version:
        version = get_local_version() or "unknown"
        print(f"A2P_Cli version {version}")
        return
    if args.check_update:
        check_for_update()
        return

    input_path = Path(args.input_dir)
    if input_path.is_file() and args.chk_bit:
        try:
            with Image.open(input_path) as img:
                n_colors, bit_count = get_real_bit_count(img)
                print(f"[CHK_BIT] {input_path.name}: {n_colors} colors, ~{bit_count} bits")
        except Exception as e:
            print(f"Error reading {input_path}: {e}")
        sys.exit(0)

    check_for_update()
    if args.chk_bit:
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
