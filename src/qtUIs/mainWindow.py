# -*- coding: utf-8 -*-

from PySide6 import QtWidgets, QtGui
from src.qtUIs.mainUI import MainUI
from src.qtUIs.calibrationUI import CalibrationUI
from src.managers.configManager import ConfigManager
from src.managers.sensorManager import SensorManager
from src.enums.uiResources import ImagePaths


class MainMenu(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Force platform reader")
        self.setWindowIcon(QtGui.QIcon(ImagePaths.WINDOW_ICON.value))
        self.setGeometry(100, 100, 1920, 1080)

        stacked_widget = QtWidgets.QStackedWidget()
        config_manager = ConfigManager()
        sensor_manager = SensorManager()

        # Define UIs and connect signals
        self.mainUI = MainUI(stacked_widget, config_manager, sensor_manager)
        self.calibrationUI = CalibrationUI(
            stacked_widget, config_manager, sensor_manager
        )
        self.mainUI.close_menu.connect(self.close)
        stacked_widget.currentChanged.connect(self.stackChangeHandler)

        # Set stacked widgets
        stacked_widget.addWidget(self.mainUI)
        stacked_widget.addWidget(self.calibrationUI)
        self.setCentralWidget(stacked_widget)

    def stackChangeHandler(self, index: int) -> None:
        if index == 1:
            self.calibrationUI.updateUI()
