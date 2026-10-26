import sys
import os
import json
from PyQt6.QtWidgets import QApplication
# from ClientUI.01_FirstScreen_Ext import LoginWindow
class MyApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)
        # self.main_window = LoginWindow()
        self.main_window.show()
if __name__ == "__main__":
    app = MyApp(sys.argv)
    sys.exit(app.exec())
