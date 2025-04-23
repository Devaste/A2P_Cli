import sys
from typing import Any
from logic.convert import convert_avif_to_png
from logic.logging_config import configure_logging
from logic.update_check import check_for_update
from .config import DEFAULT_METHOD, DEFAULT_DITHER, METHOD_CHOICES, DITHER_CHOICES, OPTION_VALIDATORS
from .menu_helpers import print_option, get_validated_input, clear_screen

# Store CLI argument values globally for interactive editing
cli_args = {
    'input_dir': '',
    'output_dir': None,
    'replace': False,
    'recursive': False,
    'silent': False,
    'qb_color': None,
    'qb_gray_color': None,
    'qb_gray': None,
    'method': DEFAULT_METHOD,
    'dither': DEFAULT_DITHER,
    'log_level': 0,
}

def get_method_str(val: Any) -> str:
    return f"{val} ({METHOD_CHOICES.get(val, 'Unknown')})" if val is not None else 'None'

def get_dither_str(val: Any) -> str:
    return f"{val} ({DITHER_CHOICES.get(val, 'Unknown')})" if val is not None else 'None'

def print_menu() -> None:
    clear_screen()
    print("\nA2P_Cli - AVIF to PNG Converter")
    print("1. Start Interactive Conversion")
    print("2. Edit Options")
    print("3. Check for Updates")
    print("0. Quit")

def get_input(prompt: str, default: Any = None) -> Any:
    val = input(f"{prompt} " + (f"[default: {default}] " if default else ""))
    return val.strip() or default

def show_options_menu() -> None:
    while True:
        clear_screen()
        print("\nEdit CLI Options:")
        print_option(1, 'input_dir', cli_args['input_dir'])
        print_option(2, 'output_dir', cli_args['output_dir'])
        print_option(3, 'replace', 'y' if cli_args['replace'] else 'n')
        print_option(4, 'recursive', 'y' if cli_args['recursive'] else 'n')
        print_option(5, 'silent', 'y' if cli_args['silent'] else 'n')
        print_option(6, 'qb_color', cli_args['qb_color'])
        print_option(7, 'qb_gray_color', cli_args['qb_gray_color'])
        print_option(8, 'qb_gray', cli_args['qb_gray'])
        print_option(9, 'method', get_method_str(cli_args['method']))
        print_option(10, 'dither', get_dither_str(cli_args['dither']))
        print_option(11, 'log_level', cli_args.get('log_level', 0))
        print("0. Back to main menu")
        choice = get_validated_input("Select an option to edit (0-11):")
        match choice:
            case "1":
                cli_args['input_dir'] = get_validated_input(
                    "Enter input directory:", cli_args['input_dir'], OPTION_VALIDATORS['input_dir'])
            case "2":
                cli_args['output_dir'] = get_validated_input(
                    "Enter output directory (leave blank for same as input):", cli_args['output_dir'], OPTION_VALIDATORS['output_dir']) or None
            case "3":
                val = get_validated_input("Replace originals? (y/n):", 'y' if cli_args['replace'] else 'n', OPTION_VALIDATORS['replace'])
                cli_args['replace'] = val.lower() == 'y' if isinstance(val, str) else bool(val)
            case "4":
                val = get_validated_input("Recursive search? (y/n):", 'y' if cli_args['recursive'] else 'n', OPTION_VALIDATORS['recursive'])
                cli_args['recursive'] = val.lower() == 'y' if isinstance(val, str) else bool(val)
            case "5":
                val = get_validated_input("Silent mode? (y/n):", 'y' if cli_args['silent'] else 'n', OPTION_VALIDATORS['silent'])
                cli_args['silent'] = val.lower() == 'y' if isinstance(val, str) else bool(val)
            case "6":
                val = get_validated_input("Quantization bits for color images (1-8, blank for default):", cli_args['qb_color'], OPTION_VALIDATORS['qb_color'])
                cli_args['qb_color'] = int(val) if val else None
            case "7":
                val = get_validated_input("Quantization bits for grayscale+one images (1-8, blank for default):", cli_args['qb_gray_color'], OPTION_VALIDATORS['qb_gray_color'])
                cli_args['qb_gray_color'] = int(val) if val else None
            case "8":
                val = get_validated_input("Quantization bits for grayscale images (1-8, blank for default):", cli_args['qb_gray'], OPTION_VALIDATORS['qb_gray'])
                cli_args['qb_gray'] = int(val) if val else None
            case "9":
                val = get_validated_input("Quantization method (0=Median Cut, 1=Max Coverage, 2=Fast Octree):", cli_args['method'], OPTION_VALIDATORS['method'])
                cli_args['method'] = int(val)
            case "10":
                val = get_validated_input("Dither (0=None, 1=Floyd-Steinberg):", cli_args['dither'], OPTION_VALIDATORS['dither'])
                cli_args['dither'] = int(val)
            case "11":
                val = get_validated_input("Logging level (0=off, 1=error, 2=warning, 3=info, 4=debug):", cli_args.get('log_level', 0), lambda v: str(v) in ['0','1','2','3','4'])
                cli_args['log_level'] = int(val)
            case "0":
                break
            case _:
                print("Invalid option. Please enter a number between 0 and 11.")

def convert_menu() -> None:
    clear_screen()
    convert_avif_to_png(
        cli_args['input_dir'],
        cli_args['output_dir'],
        replace=cli_args['replace'],
        recursive=cli_args['recursive'],
        silent=cli_args['silent'],
        qb_color=cli_args['qb_color'],
        qb_gray_color=cli_args['qb_gray_color'],
        qb_gray=cli_args['qb_gray'],
        **{k: v for k, v in cli_args.items() if k not in ['input_dir', 'output_dir', 'replace', 'recursive', 'silent', 'qb_color', 'qb_gray_color', 'qb_gray']}
    )

def run() -> None:
    while True:
        print_menu()
        choice = get_validated_input("Choose an option (0-3):")
        match choice:
            case "1":
                configure_logging(cli_args.get('log_level', 0))
                convert_menu()
            case "2":
                show_options_menu()
            case "3":
                check_for_update()
                input("Press Enter to return to menu...")
            case "0":
                print("Exiting.")
                sys.exit(0)
            case _:
                print("Invalid option. Please enter 0, 1, 2, or 3.")

if __name__ == "__main__":
    run()
