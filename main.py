# Clear log file at app launch
with open("a2pcli.log", "w"): pass

import logging
logging.basicConfig(
    filename="a2pcli.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)

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
