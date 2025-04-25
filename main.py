import sys

from cli.main_menu import run as main_menu_run
from cli.script_mode_utils import run_script_mode

def main():
    if len(sys.argv) == 1:
        main_menu_run()
    else:
        run_script_mode()

if __name__ == "__main__":
    main()
