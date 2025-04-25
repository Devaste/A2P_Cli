from cli.args import parse_cli_args
from cli.options_io import load_options, save_options
from logic.convert import convert_avif_to_png, get_real_bit_count
from pathlib import Path
from PIL import Image
import sys
from logic.logging_config import log_call

@log_call
def handle_options_logic(args):
    if args.get('options', False):
        file_opts = load_options('CLI')
        for k, v in file_opts.items():
            if k != 'input_dir' and (args.get(k) is None or args.get(k) == '' or args.get(k) is False):
                args[k] = v
    return args

@log_call
def handle_save_logic(args):
    if args.get('save', False):
        save_dict = {k: v for k, v in args.items() if k not in ('save', 'options')}
        save_options('CLI', save_dict)
        print("[INFO] CLI options saved to [CLI] block in options.ini.")
        sys.exit(0)

@log_call
def handle_version_check(args):
    if args.get('version', False):
        from logic.update_check import get_local_version
        print(f"A2P_Cli version: {get_local_version()}")
        sys.exit(0)

@log_call
def handle_update_check(args):
    if args.get('check_update', False):
        from logic.update_check import get_local_version, get_latest_version
        local = get_local_version()
        latest = get_latest_version()
        if latest == local:
            print(f"You are running the latest version: {local}.")
        else:
            print(f"Update available: {latest} (You have {local})")
        sys.exit(0)

@log_call
def handle_bit_check(args):
    input_path = Path(args['input_dir'])
    if input_path.is_file() and args.get('chk_bit', False):
        try:
            with Image.open(input_path) as img:
                n_colors, bit_count = get_real_bit_count(img)
                print(f"[CHK_BIT] {input_path.name}: {n_colors} colors, ~{bit_count} bits")
        except Exception as e:
            print(f"Error reading {input_path}: {e}")
        sys.exit(0)

@log_call
def run_conversion(args):
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
    if not args['silent']:
        if result is not None and isinstance(result, dict):
            print(f"Conversion finished. Success: {result.get('success', 0)}, Failed: {result.get('fail', 0)}")
        else:
            print("Conversion finished.")

@log_call
def run():
    args = parse_cli_args()
    if args is None:
        print("[Error] No CLI arguments provided.")
        sys.exit(1)
    args = handle_options_logic(args)
    handle_save_logic(args)
    handle_version_check(args)
    handle_update_check(args)
    handle_bit_check(args)
    run_conversion(args)
