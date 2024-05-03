# -*- coding: utf-8 -*-

from src.enums.qssLabels import QssLabels
from src.enums.uiResources import ImagePaths, IconPaths
from src.managers.configManager import ConfigManager
from src.managers.sensorManager import SensorManager
from src.qtUIs.widgets.mainWidgets import CalibrationSelector
from src.qtUIs.widgets import customQtLoaders as customQT
from PySide6 import QtWidgets, QtGui, QtCore


class CalibrationUI(QtWidgets.QWidget):
    def __init__(
        self,
        stacked_widget: QtWidgets.QStackedWidget,
        config_manager: ConfigManager,
        sensor_manager: SensorManager,
    ):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.cfg_mngr = config_manager
        self.sensor_mngr = sensor_manager

        # self.initManagers() TODO
        self.initUI()
        # self.getSensorInformation() TODO

    def updateUI(self) -> None:
        self.calibration_selector.updateLayouts(self.sensor_mngr.getPlatformGroups())
        # TODO
        # self.initManagers()
        # self.calib_widget.loadManager(self.calib_mngr)
        # self.getSensorInformation()
        pass

    def initManagers(self) -> None:
        # self.calib_mngr = CalibrationManager(self.cfg_mngr, self.sensor_mngr)
        pass

    def initUI(self):
        self.main_layout = QtWidgets.QHBoxLayout()

        # Load UI layouts
        # self.calib_widget = CalibrationPanelWidget() TODO
        self.settings_panel = self.loadInfoPanel()

        self.main_layout.addWidget(self.settings_panel)
        self.main_layout.addWidget(QtWidgets.QWidget())  # TODO calib panel

        self.setLayout(self.main_layout)

    # UI buttons click connectors

    @QtCore.Slot()
    def calibratePlatform(self):
        platform_name = self.platform_selector.currentText()
        if platform_name is None:
            return
        # TODO
        pass

    @QtCore.Slot()
    def calibrateSensor(self):
        sensor_name = self.sensor_selector.currentText()
        if sensor_name is None:
            return
        # TODO
        pass

    @QtCore.Slot()
    def goToMainUI(self):
        self.stacked_widget.setCurrentIndex(0)

    # UI section loaders

    def loadInfoPanel(self) -> QtWidgets.QWidget:
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)
        # Container to fix width of control panel
        container = QtWidgets.QWidget()
        container.setLayout(vbox_layout)
        container.setFixedWidth(250)
        # Top images grid
        image_logo = QtWidgets.QLabel(self)
        image_platform = QtWidgets.QLabel(self)
        pixmap_logo = QtGui.QPixmap(ImagePaths.LOGO.value)
        pixmap_platform = QtGui.QPixmap(ImagePaths.PLATFORM.value)
        pixmap_platform.scaledToWidth(220)
        image_logo.setPixmap(pixmap_logo)
        image_logo.setAlignment(QtCore.Qt.AlignCenter)
        image_platform.setPixmap(pixmap_platform.scaledToWidth(250))
        image_platform.setAlignment(QtCore.Qt.AlignCenter)
        # Buttons
        self.close_button = customQT.createQPushButton(
            "Return to main window",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=True,
            connect_fn=self.goToMainUI,
        )
        self.platform_calibrate_button = customQT.createQPushButton(
            "Calibrate platform",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=False,
            connect_fn=self.calibratePlatform,
        )
        self.sensor_calibrate_button = customQT.createQPushButton(
            "Calibrate sensor",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=False,
            connect_fn=self.calibrateSensor,
        )
        # Platform and sensor selector
        self.platform_selector = QtWidgets.QComboBox()
        self.sensor_selector = QtWidgets.QComboBox()
        self.calibration_selector = CalibrationSelector()
        self.calibration_selector.setupLayouts(
            self.platform_selector, self.sensor_selector
        )
        # Author and version label
        credits_layout = QtWidgets.QHBoxLayout()
        credits_layout.setAlignment(QtCore.Qt.AlignLeft)
        github_icon = customQT.createIconLabelBox(IconPaths.GITHUB, None)
        tag_icon = customQT.createIconLabelBox(IconPaths.TAG, None)
        author_label = customQT.createLabelBox(
            "AaronPB", QssLabels.AUTHOR_COPYRIGHT_LABEL
        )
        version_label = customQT.createLabelBox(
            "PRE-v.1.2", QssLabels.AUTHOR_COPYRIGHT_LABEL
        )
        credits_layout.addWidget(github_icon)
        credits_layout.addWidget(author_label)
        credits_layout.addWidget(tag_icon)
        credits_layout.addWidget(version_label)

        # Build layout
        vbox_layout.addWidget(image_logo)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(QtWidgets.QLabel("Platform layout"))
        vbox_layout.addWidget(image_platform)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(QtWidgets.QLabel("Select platform"))
        vbox_layout.addWidget(self.platform_selector)
        vbox_layout.addWidget(self.platform_calibrate_button)
        vbox_layout.addItem(QtWidgets.QSpacerItem(10, 10))
        vbox_layout.addWidget(QtWidgets.QLabel("Select sensor"))
        vbox_layout.addWidget(self.sensor_selector)
        vbox_layout.addWidget(self.sensor_calibrate_button)
        vbox_layout.addItem(
            QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
        )
        vbox_layout.addWidget(self.close_button)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addLayout(credits_layout)
        return container
