# -*- coding: utf-8 -*-

import sys
from src.qtUIs.mainWindow import MainMenu
from PySide6 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(open("src/qtUIs/style.qss").read())
    window = MainMenu()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
