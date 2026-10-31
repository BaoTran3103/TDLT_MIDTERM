import sys
import os
import importlib

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

SCREEN_DIR = os.path.join(CURRENT_DIR, "Client", "ClientUI", "01_MainScreen")
if SCREEN_DIR not in sys.path:
    sys.path.insert(0, SCREEN_DIR)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

# Import class MainScreen_Ext từ module 01_MainScreen_Ext
ext_module = importlib.import_module("01_MainScreen_Ext")
MainScreen_Ext = ext_module.MainScreen_Ext


class MyApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        app_font = QFont("SF Pro Display", 10)
        app_font.setStyleHint(QFont.StyleHint.SansSerif)
        self.setFont(app_font)
        
        self.main_window = MainScreen_Ext()
        self.main_window.resize(1440, 900)
        self.main_window.show()


if __name__ == "__main__":
    app = MyApp(sys.argv)
    sys.exit(app.exec())
