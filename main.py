# Clear log file at app launch
with open("a2pcli.log", "w") as f:
    f.write("")

import logging
logging.basicConfig(
    filename="a2pcli.log",
    filemode="a",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)

import sys

def main():
    """
    Entry point for A2P_Cli.
    Runs TUI if no arguments are given, otherwise runs CLI/script mode.
    """
    if len(sys.argv) == 1:
        from gui.qt_app import run as main_menu_run
        main_menu_run()
    else:
        from cli.script_mode import run as script_mode_run
        script_mode_run()

if __name__ == "__main__":
    main()
