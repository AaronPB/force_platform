# -*- coding: utf-8 -*-

from src.enums.qssLabels import QssLabels
from src.managers.configManager import ConfigManager
from src.managers.calibrationManager import CalibrationManager
from src.sensorLoader import SensorLoader
from src.qtUIs.widgets import customQtLoaders as customQT
from src.qtUIs.widgets.calibrationPanelWidget import CalibrationPanelWidget
from PySide6 import QtWidgets, QtGui, QtCore


class CalibrationUI(QtWidgets.QWidget):
    def __init__(
        self,
        stacked_widget: QtWidgets.QStackedWidget,
        config_manager: ConfigManager,
        sensor_loader: SensorLoader,
        logo_image_path: str,
        platform_image_path: str,
    ):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.cfg_mngr = config_manager
        self.sensor_loader = sensor_loader
        self.logo_img_path = logo_image_path
        self.platform_img_path = platform_image_path

        self.initManagers()
        self.initUI()
        self.getSensorInformation()

    def updateUI(self) -> None:
        self.initManagers()
        self.getSensorInformation()

    def initManagers(self) -> None:
        self.calib_mngr = CalibrationManager(self.cfg_mngr, self.sensor_loader)

    def initUI(self):
        self.main_layout = QtWidgets.QHBoxLayout()

        # Load UI layouts
        self.calib_widget = CalibrationPanelWidget(self.calib_mngr)
        self.settings_panel = self.loadInfoPanel()

        self.main_layout.addWidget(self.settings_panel)
        self.main_layout.addWidget(self.calib_widget)

        self.setLayout(self.main_layout)

    # UI buttons click connectors

    @QtCore.Slot()
    def connectSensors(self):
        self.sensors_connect_button.setEnabled(False)
        self.sensors_connection_progressbar.setValue(50)
        self.calib_mngr.checkConnection()
        self.sensors_connection_progressbar.setValue(100)
        self.getSensorInformation()
        self.sensors_connection_progressbar.setValue(0)
        # self.updateTestStatus()
        self.sensors_connect_button.setEnabled(True)

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
        # container.setFixedWidth(600)
        # Top images grid
        imgs_grid_layout = QtWidgets.QGridLayout()
        image_logo = QtWidgets.QLabel(self)
        image_platform = QtWidgets.QLabel(self)
        pixmap_logo = QtGui.QPixmap(self.logo_img_path)
        pixmap_platform = QtGui.QPixmap(self.platform_img_path)
        image_logo.setPixmap(pixmap_logo)
        image_logo.setAlignment(QtCore.Qt.AlignCenter)
        image_platform.setPixmap(
            pixmap_platform.scaled(300, 300, QtCore.Qt.KeepAspectRatio)
        )
        image_platform.setAlignment(QtCore.Qt.AlignCenter)
        imgs_grid_layout.addWidget(image_logo, 0, 0)
        imgs_grid_layout.addWidget(image_platform, 0, 1)
        # Buttons
        self.close_button = customQT.createQPushButton(
            "Return to main window",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=True,
            connect_fn=self.goToMainUI,
        )
        # Author label
        author_label = customQT.createLabelBox(
            "© github.AaronPB", QssLabels.AUTHOR_COPYRIGHT_LABEL
        )

        # Build layout
        vbox_layout.addLayout(imgs_grid_layout)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(self.loadSensorContainer())
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(self.close_button)
        vbox_layout.addItem(
            QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
        )
        vbox_layout.addWidget(author_label)
        return container

    def loadSensorContainer(self) -> QtWidgets.QWidget:
        sensors_group_box = QtWidgets.QGroupBox("Sensor information")
        sensors_vbox_layout = QtWidgets.QVBoxLayout()
        sensors_group_box.setLayout(sensors_vbox_layout)
        sensors_vbox_layout.setAlignment(QtCore.Qt.AlignTop)
        # - Connection button and progress bar
        connect_grid_layout = QtWidgets.QGridLayout()
        self.sensors_connect_button = customQT.createQPushButton(
            "Connect sensors", enabled=True, connect_fn=self.connectSensors
        )
        self.sensors_connection_progressbar = QtWidgets.QProgressBar()
        self.sensors_connection_progressbar.setValue(0)
        connect_grid_layout.addWidget(self.sensors_connect_button, 0, 0)
        connect_grid_layout.addWidget(self.sensors_connection_progressbar, 0, 1)
        # - Sensors grid
        sensors_grid_layout = QtWidgets.QGridLayout()
        group_box_platform1 = QtWidgets.QGroupBox("Platform 1")
        group_box_platform2 = QtWidgets.QGroupBox("Platform 2")
        self.vbox_platform1 = QtWidgets.QVBoxLayout()
        self.vbox_platform2 = QtWidgets.QVBoxLayout()
        self.vbox_platform1.setAlignment(QtCore.Qt.AlignTop)
        self.vbox_platform2.setAlignment(QtCore.Qt.AlignTop)
        group_box_platform1.setLayout(self.vbox_platform1)
        group_box_platform2.setLayout(self.vbox_platform2)
        sensors_grid_layout.addWidget(group_box_platform1, 0, 0)
        sensors_grid_layout.addWidget(group_box_platform2, 0, 1)
        # Build sensor information layout
        sensors_vbox_layout.addLayout(connect_grid_layout)
        sensors_vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        sensors_vbox_layout.addLayout(sensors_grid_layout)

        return sensors_group_box

    # Functions to load information

    def getSensorInformation(self):
        self.setSensorBox(
            self.vbox_platform1,
            self.calib_mngr.getP1SensorStatus(),
            self.calib_widget.selectPlatformSensor,
            platform=1,
        )
        self.setSensorBox(
            self.vbox_platform2,
            self.calib_mngr.getP2SensorStatus(),
            self.calib_widget.selectPlatformSensor,
            platform=2,
        )

    def setSensorBox(
        self,
        vbox_layout: QtWidgets.QVBoxLayout,
        sensor_dict: dict,
        update_fn,
        platform: int,
    ):
        # Clear layout
        for i in reversed(range(vbox_layout.count())):
            widget = vbox_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        # Add new widgets
        for index, sensor_list in enumerate(sensor_dict.values()):
            button = customQT.createSensorQPushButton(
                sensor_list[0] + " (" + sensor_list[1] + ")",
                sensor_list[2].value,
                connect_fn=update_fn,
                index=index,
                platform=platform,
            )
            vbox_layout.addWidget(button)
