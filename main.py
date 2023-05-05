# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import sys
from PyQt5.QtWidgets import QApplication
from src.interface import MainWindow


class Main:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.menu = MainWindow()

    def run(self):
        self.menu.show()
        sys.exit(self.app.exec_())


if __name__ == '__main__':
    app = Main()
    app.run()
