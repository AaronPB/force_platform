# -*- coding: utf-8 -*-

import sys
from src.qtUIs.mainUI import MainUI
from PySide6 import QtWidgets


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(open("src/qtUIs/style.qss").read())
    window = MainUI()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
