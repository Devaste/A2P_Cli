import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from .qt_main_window import MainWindow
import os

def run():
    app = QApplication(sys.argv)
    app.setApplicationName("A2P_Cli")
    # Use icon.ico from the project root
    icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'icon.ico'))
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    window = MainWindow()
    window.show()
    app.exec_()
