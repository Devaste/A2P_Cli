import sys
from logic.update_check import check_for_update

check_for_update()

from cli.menu import run

if __name__ == "__main__":
    run()
