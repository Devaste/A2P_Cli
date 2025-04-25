from cli.args import parse_cli_args
from cli.options_io import load_options, save_options
from logic.convert import convert_avif_to_png, get_real_bit_count
from pathlib import Path
from PIL import Image
import sys

def run():
    args = parse_cli_args()
    if args is None:
        print("[Error] No CLI arguments provided.")
        sys.exit(1)

    # Handle --save and --options logic
    if args.get('options', False):
        # Load CLI options from file, but always use provided input_dir if given
        file_opts = load_options('CLI')
        # Only override if not provided in CLI
        for k, v in file_opts.items():
            if k != 'input_dir' and (args.get(k) is None or args.get(k) == '' or args.get(k) == False):
                args[k] = v
    if args.get('save', False):
        # Save current CLI args (except --save/--options themselves)
        save_dict = {k: v for k, v in args.items() if k not in ('save', 'options')}
        save_options('CLI', save_dict)
        print("[INFO] CLI options saved to [CLI] block in options.ini.")
        sys.exit(0)
    if args.get('version', False):
        from logic.update_check import get_local_version
        print(f"A2P_Cli version: {get_local_version()}")
        return
    if args.get('check_update', False):
        from logic.update_check import get_local_version, get_latest_version
        local = get_local_version()
        latest = get_latest_version()
        if latest == local:
            print(f"You are running the latest version: {local}.")
        else:
            print(f"Update available: {latest} (You have {local})")
        return
    input_path = Path(args['input_dir'])
    if input_path.is_file() and args.get('chk_bit', False):
        try:
            with Image.open(input_path) as img:
                n_colors, bit_count = get_real_bit_count(img)
                print(f"[CHK_BIT] {input_path.name}: {n_colors} colors, ~{bit_count} bits")
        except Exception as e:
            print(f"Error reading {input_path}: {e}")
        sys.exit(0)
    result = convert_avif_to_png(
        args['input_dir'],
        output_dir=args['output_dir'],
        remove=args['remove'],
        recursive=args['recursive'],
        silent=args['silent'],
        qb_color=args['qb_color'],
        qb_gray_color=args['qb_gray_color'],
        qb_gray=args['qb_gray'],
        method=args['method'],
        dither=args['dither'],
        chk_bit=args['chk_bit'],
        progress_printer=print
    )
    # Print summary unless silent
    if not args['silent']:
        if result is not None and isinstance(result, dict):
            print(f"Conversion finished. Success: {result.get('success', 0)}, Failed: {result.get('fail', 0)}")
        else:
            print("Conversion finished.")
