import sys

from cli.tui_mode import run as main_menu_run
from cli.script_mode import run as script_mode_run

def main():
    if len(sys.argv) == 1:
        main_menu_run()
    else:
        script_mode_run()

if __name__ == "__main__":
    main()
