import sys
import argparse
from logic.update_check import check_for_update, get_local_version
from cli.menu import run

def main():
    parser = argparse.ArgumentParser(description="A2P_Cli: AVIF to PNG Converter")
    parser.add_argument('--version', action='store_true', help='Show version and exit')
    parser.add_argument('--check-update', action='store_true', help='Check for updates and exit')
    args = parser.parse_args()

    if args.version:
        version = get_local_version() or "unknown"
        print(f"A2P_Cli version {version}")
        sys.exit(0)
    if args.check_update:
        check_for_update()
        sys.exit(0)

    # Default: run the main menu
    check_for_update()
    run()

if __name__ == "__main__":
    main()
