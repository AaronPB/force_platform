# -*- coding: utf-8 -*-

import os
from PySide6 import QtWidgets, QtGui, QtCore
from src.qtUIs.mainUI import MainUI
from src.qtUIs.calibrationUI import CalibrationUI
from src.managers.configManager import ConfigManager


class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.images_folder = os.path.join(
            os.path.dirname(__file__), "..", "..", "images"
        )
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Force platform reader")
        self.setWindowIcon(QtGui.QIcon(os.path.join(self.images_folder, "logo.ico")))
        self.setGeometry(100, 100, 1920, 1080)

        stacked_widget = QtWidgets.QStackedWidget()
        logo_path = os.path.join(self.images_folder, "mainUI_logo.svg")
        config_manager = ConfigManager()

        # Define UIs and connect signals
        self.mainUI = MainUI(stacked_widget, config_manager, logo_path)
        self.calibrationUI = CalibrationUI(stacked_widget, config_manager, logo_path)
        self.mainUI.close_menu.connect(self.close)

        # Set stacked widgets
        stacked_widget.addWidget(self.mainUI)
        stacked_widget.addWidget(self.calibrationUI)
        self.setCentralWidget(stacked_widget)
