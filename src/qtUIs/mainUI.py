# -*- coding: utf-8 -*-

import os

from src.enums.qssLabels import QssLabels
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.managers.configManager import ConfigManager
from src.managers.testManager import TestManager
from PySide6 import QtWidgets, QtGui, QtCore


class MainUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.images_folder = os.path.join(
            os.path.dirname(__file__), '..', '..', 'images')
        self.initManagers()
        self.initUI()
        self.updateTestStatus()
        self.getSensorInformation()

    def initManagers(self) -> None:
        self.cfg_mngr = ConfigManager()
        self.test_mngr = TestManager(self.cfg_mngr)

    def initUI(self) -> None:
        self.setWindowTitle('Force platform reader')
        self.setWindowIcon(QtGui.QIcon(
            os.path.join(self.images_folder, 'logo.ico')))
        self.setGeometry(100, 100, 1920, 1080)

        self.main_layout = QtWidgets.QHBoxLayout()

        # Load UI layouts
        self.cp_container = self.loadControlPanelContainer()
        tabular_widget = self.loadTabularPanel()

        self.main_layout.addWidget(self.cp_container)
        self.main_layout.addWidget(tabular_widget)

        self.setLayout(self.main_layout)
        self.show()

    # UI generic widgets setup methods

    def createLabelBox(self, text: str, qss_object: QssLabels = None) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(text)
        if qss_object is not None:
            label.setObjectName(qss_object.value)
        return label

    def createQPushButton(self, title: str, qss_object: QssLabels = None,
                          enabled: bool = False, connect_fn=None) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(title)
        if qss_object is not None:
            button.setObjectName(qss_object.value)
        button.setEnabled(enabled)
        if connect_fn is not None:
            button.clicked.connect(connect_fn)
        return button

    def createSensorQCheckBox(self, text: str, qss_object: QssLabels = None,
                              enabled: bool = True) -> QtWidgets.QCheckBox:
        checkbox = QtWidgets.QCheckBox(text)
        if qss_object is not None:
            checkbox.setObjectName(qss_object.value)
        checkbox.setEnabled(enabled)
        return checkbox

    # UI buttons click connectors

    def startTest(self):
        pass

    def stopTest(self):
        pass

    def tareSensors(self):
        pass

    def calibrateSensors(self):
        pass

    def setConfigFile(self) -> None:
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        config_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select file', '', 'yaml file (*.yaml)', options=options)
        if config_file_path:
            self.cfg_mngr.loadConfigFile(config_file_path)
        self.updateTestStatus()

    def setTestFolder(self):
        pass

    def setTestName(self):
        pass

    def connectSensors(self):
        pass

    # UI section loaders

    def loadControlPanelContainer(self) -> QtWidgets.QWidget:
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)
        # Container to fix width of control panel
        container = QtWidgets.QWidget()
        container.setLayout(vbox_layout)
        container.setFixedWidth(250)
        # Top icon
        image = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(os.path.join(self.images_folder, 'logo.ico'))
        image.setPixmap(pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio))
        image.setAlignment(QtCore.Qt.AlignCenter)
        # Title label
        software_title = self.createLabelBox(
            'Force Platform Reader', QssLabels.TITLE_LABEL)
        software_title.setAlignment(QtCore.Qt.AlignCenter)
        # Status label
        status_group_box = QtWidgets.QGroupBox('Status Information')
        self.status_vbox_layout = QtWidgets.QVBoxLayout()
        status_group_box.setLayout(self.status_vbox_layout)
        self.status_label = self.createLabelBox(
            'Loading ...', QssLabels.STATUS_LABEL_WARN)
        self.status_vbox_layout.addWidget(self.status_label)
        # Buttons
        buttons_group_box = QtWidgets.QGroupBox('Control Panel')
        buttons_vbox_layout = QtWidgets.QVBoxLayout()
        buttons_group_box.setLayout(buttons_vbox_layout)
        self.start_button = self.createQPushButton(
            'Start test', QssLabels.CONTROL_PANEL_BTN, connect_fn=self.startTest)
        self.stop_button = self.createQPushButton(
            'Stop test', QssLabels.CONTROL_PANEL_BTN, connect_fn=self.stopTest)
        self.tare_button = self.createQPushButton(
            'Tare test', QssLabels.CONTROL_PANEL_BTN, connect_fn=self.tareSensors)
        self.calibration_button = self.createQPushButton(
            'Calibrate sensors', QssLabels.CONTROL_PANEL_BTN, connect_fn=self.calibrateSensors)
        self.close_button = self.createQPushButton(
            'Close', QssLabels.CONTROL_PANEL_BTN, enabled=True, connect_fn=self.close)
        buttons_vbox_layout.addWidget(self.start_button)
        buttons_vbox_layout.addWidget(self.tare_button)
        buttons_vbox_layout.addWidget(self.stop_button)
        buttons_vbox_layout.addWidget(self.calibration_button)
        # Author label
        author_label = self.createLabelBox(
            '© github.AaronPB', QssLabels.AUTHOR_COPYRIGHT_LABEL)

        # Build layout
        vbox_layout.addWidget(image)
        vbox_layout.addWidget(software_title)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(status_group_box)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(buttons_group_box)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(self.close_button)
        vbox_layout.addItem(QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding))
        vbox_layout.addWidget(author_label)
        return container

    def loadTabularPanel(self) -> QtWidgets.QTabWidget:
        tabular_panel = QtWidgets.QTabWidget()
        tabular_panel.addTab(self.loadTabSettings(),
                             'Settings and sensor information')
        tabular_panel.addTab(self.loadTabPlatformPlots(),
                             'Platform plots')
        tabular_panel.addTab(self.loadTabCOPPlots(),
                             'COP plots')
        tabular_panel.addTab(self.loadTabEncoderPlots(),
                             'Encoder plots')
        tabular_panel.addTab(self.loadTabIMUPlots(),
                             'IMU plots')
        return tabular_panel

    def loadTabSettings(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        vbox_general_layout = QtWidgets.QVBoxLayout()
        tab_widget.setLayout(vbox_general_layout)
        vbox_general_layout.setAlignment(QtCore.Qt.AlignTop)

        # File management
        settings_group_box = QtWidgets.QGroupBox('File settings')
        settings_grid_layout = QtWidgets.QGridLayout()
        settings_group_box.setLayout(settings_grid_layout)
        settings_grid_layout.setAlignment(QtCore.Qt.AlignTop)
        # - Config file
        config_label = self.createLabelBox('Configuration file:')
        config_button = self.createQPushButton(
            'Select config file', enabled=True, connect_fn=self.setConfigFile)
        self.config_path = QtWidgets.QLineEdit(self)
        self.config_path.setReadOnly(True)
        # - Test folder
        test_folder_label = self.createLabelBox('Test folder path:')
        test_folder_button = self.createQPushButton(
            'Select folder', enabled=True, connect_fn=self.setTestFolder)
        self.test_folder_path = QtWidgets.QLineEdit(self)
        self.test_folder_path.setReadOnly(True)
        # - Test name
        test_name_label = self.createLabelBox('Test name:')
        test_name_button = self.createQPushButton(
            'Save name', enabled=True, connect_fn=self.setTestName)
        self.test_name_input = QtWidgets.QLineEdit(self)
        # Build grid layout
        settings_grid_layout.addWidget(config_label, 0, 0)
        settings_grid_layout.addWidget(self.config_path, 0, 1)
        settings_grid_layout.addWidget(config_button, 0, 2)
        settings_grid_layout.addWidget(test_folder_label, 1, 0)
        settings_grid_layout.addWidget(self.test_folder_path, 1, 1)
        settings_grid_layout.addWidget(test_folder_button, 1, 2)
        settings_grid_layout.addWidget(test_name_label, 2, 0)
        settings_grid_layout.addWidget(self.test_name_input, 2, 1)
        settings_grid_layout.addWidget(test_name_button, 2, 2)

        # Sensor table information
        sensors_group_box = QtWidgets.QGroupBox('Sensor information')
        sensors_vbox_layout = QtWidgets.QVBoxLayout()
        sensors_group_box.setLayout(sensors_vbox_layout)
        sensors_vbox_layout.setAlignment(QtCore.Qt.AlignTop)
        # - Connection button and progress bar
        connect_grid_layout = QtWidgets.QGridLayout()
        self.sensors_connect_button = self.createQPushButton(
            'Connect selected sensors', enabled=True, connect_fn=self.connectSensors)
        self.sensors_connection_progressbar = QtWidgets.QProgressBar()
        self.sensors_connection_progressbar.setValue(0)
        connect_grid_layout.addWidget(self.sensors_connect_button, 0, 0)
        connect_grid_layout.addWidget(
            self.sensors_connection_progressbar, 0, 1)
        # - Sensors grid
        sensors_grid_layout = QtWidgets.QGridLayout()
        group_box_platform1 = QtWidgets.QGroupBox('Platform 1')
        group_box_platform2 = QtWidgets.QGroupBox('Platform 2')
        group_box_external = QtWidgets.QGroupBox('External Sensors')
        self.vbox_platform1 = QtWidgets.QVBoxLayout()
        self.vbox_platform2 = QtWidgets.QVBoxLayout()
        self.vbox_external = QtWidgets.QVBoxLayout()
        self.vbox_platform1.setAlignment(QtCore.Qt.AlignTop)
        self.vbox_platform2.setAlignment(QtCore.Qt.AlignTop)
        self.vbox_external.setAlignment(QtCore.Qt.AlignTop)
        group_box_platform1.setLayout(self.vbox_platform1)
        group_box_platform2.setLayout(self.vbox_platform2)
        group_box_external.setLayout(self.vbox_external)
        sensors_grid_layout.addWidget(group_box_platform1, 0, 0)
        sensors_grid_layout.addWidget(group_box_platform2, 0, 1)
        sensors_grid_layout.addWidget(group_box_external, 0, 2)
        # Build sensor information layout
        sensors_vbox_layout.addLayout(connect_grid_layout)
        sensors_vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        sensors_vbox_layout.addLayout(sensors_grid_layout)

        # Build main tab vbox
        vbox_general_layout.addWidget(settings_group_box)
        vbox_general_layout.addItem(QtWidgets.QSpacerItem(40, 40))
        vbox_general_layout.addWidget(sensors_group_box)

        return tab_widget

    def loadTabPlatformPlots(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        # TODO
        return tab_widget

    def loadTabCOPPlots(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        # TODO
        return tab_widget

    def loadTabEncoderPlots(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        # TODO
        return tab_widget

    def loadTabIMUPlots(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        # TODO
        return tab_widget

    # Functions to load information

    def updateTestStatus(self) -> None:
        status_text = ''
        self.config_path.setText(self.cfg_mngr.getCurrentFilePath())
        test_folder = self.cfg_mngr.getConfigValue(
            CfgPaths.GENERAL_TEST_FOLDER.value)
        test_name = self.cfg_mngr.getConfigValue(
            CfgPaths.GENERAL_TEST_NAME.value)
        if test_folder is not None:
            self.test_folder_path.setText(test_folder)
        if test_folder is None:
            status_text = 'Provide a test folder!'
        if test_name is not None:
            self.test_name_input.setText(test_name)
        if test_name is None:
            if status_text != '':
                status_text = status_text + '\n'
            status_text = status_text + 'Provide a test name!'

        if status_text == '':
            self.status_label.setParent(None)
            self.status_label = self.createLabelBox(
                'Requirements OK', QssLabels.STATUS_LABEL_OK)
            self.status_vbox_layout.addWidget(self.status_label)
            return
        self.status_label.setText(status_text)
        self.status_label.setObjectName(QssLabels.STATUS_LABEL_WARN.value)

    def getSensorInformation(self):
        self.setSensorBox(self.vbox_platform1,
                          self.test_mngr.getP1SensorStatus())
        self.setSensorBox(self.vbox_platform2,
                          self.test_mngr.getP2SensorStatus())
        self.setSensorBox(self.vbox_external,
                          self.test_mngr.getOthersSensorStatus())

    def setSensorBox(self, vbox_layout: QtWidgets.QVBoxLayout, sensor_dict: dict, update_fn=None):
        # Clear layout
        for widget in vbox_layout.findChildren(QtWidgets.QWidget):
            widget.setParent(None)
        # Add new widgets
        for sensor_id, sensor_list in sensor_dict.items():
            checkbox = self.createSensorQCheckBox(
                sensor_list[0] + ' (' + sensor_list[1] + ')', sensor_list[2].value)
            checkbox.setChecked(sensor_list[3])
            vbox_layout.addWidget(checkbox)
