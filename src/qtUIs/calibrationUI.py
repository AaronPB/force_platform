# -*- coding: utf-8 -*-

from src.enums.qssLabels import QssLabels
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.managers.configManager import ConfigManager
from PySide6 import QtWidgets, QtGui, QtCore


class CalibrationUI(QtWidgets.QWidget):
    def __init__(self, stacked_widget: QtWidgets.QStackedWidget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        # TODO
        layout = QtWidgets.QVBoxLayout()

        leave_button = QtWidgets.QPushButton("Volver al menú principal")
        leave_button.clicked.connect(self.toMainUI)

        layout.addWidget(leave_button)
        self.setLayout(layout)

    def toMainUI(self) -> None:
        self.stacked_widget.setCurrentIndex(0)
