# -*- coding: utf-8 -*-

from src.enums.qssLabels import QssLabels
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.managers.configManager import ConfigManager
from src.managers.testManager import TestManager
from src.managers.testFileManager import TestFileManager
from src.managers.testDataManager import TestDataManager
from src.qtUIs.threads.plotterThread import PlotterThread
from PySide6 import QtWidgets, QtGui, QtCore


class MainUI(QtWidgets.QWidget):
    close_menu = QtCore.Signal()

    def __init__(
        self,
        stacked_widget: QtWidgets.QStackedWidget,
        config_manager: ConfigManager,
        logo_image_path: str,
    ):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.cfg_mngr = config_manager
        self.logo_img_path = logo_image_path

        self.initManagers()
        self.initUI()
        self.updateTestStatus()
        self.getSensorInformation()

        self.plot_thread = PlotterThread(self.tabular_widget, self.data_mngr, 500)

    def initManagers(self) -> None:
        self.file_mngr = TestFileManager(self.cfg_mngr)
        self.test_mngr = TestManager(self.cfg_mngr)
        self.data_mngr = TestDataManager(self.test_mngr)

        self.test_timer = QtCore.QTimer(self)
        self.test_timer.timeout.connect(self.test_mngr.testRegisterValues)
        self.tare_timer = QtCore.QTimer(self)

    def initUI(self) -> None:
        self.main_layout = QtWidgets.QHBoxLayout()

        # Load UI layouts
        self.cp_container = self.loadControlPanelContainer()
        self.tabular_widget = self.loadTabularPanel()

        self.main_layout.addWidget(self.cp_container)
        self.main_layout.addWidget(self.tabular_widget)

        self.setLayout(self.main_layout)

    # UI generic widgets setup methods

    def createLabelBox(
        self, text: str, qss_object: QssLabels = None
    ) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(text)
        if qss_object is not None:
            label.setObjectName(qss_object.value)
        return label

    def createQPushButton(
        self,
        title: str,
        qss_object: QssLabels = None,
        enabled: bool = False,
        connect_fn=None,
    ) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(title)
        if qss_object is not None:
            button.setObjectName(qss_object.value)
        button.setEnabled(enabled)
        if connect_fn is not None:
            button.clicked.connect(connect_fn)
        return button

    def createSensorQCheckBox(
        self,
        text: str,
        qss_object: QssLabels = None,
        enabled: bool = True,
        change_fn=None,
        index=0,
    ) -> QtWidgets.QCheckBox:
        checkbox = QtWidgets.QCheckBox(text)
        if qss_object is not None:
            checkbox.setObjectName(qss_object.value)
        checkbox.setEnabled(enabled)
        if change_fn is not None:
            checkbox.stateChanged.connect(
                lambda state, index=index: change_fn(index, state == 2)
            )
        return checkbox

    # UI buttons click connectors

    @QtCore.Slot()
    def startTest(self):
        # Update file name in case
        self.file_mngr.checkFileName()
        self.test_name_input.setText(self.file_mngr.getFileName())
        print(f"Starting test: {self.file_mngr.getFileName()}")

        self.start_button.setEnabled(False)
        self.sensors_connect_button.setEnabled(False)
        self.calibration_button.setEnabled(False)
        self.test_mngr.testStart()
        self.tare_button.setEnabled(True)
        self.stop_button.setEnabled(True)

        self.test_timer.start(
            self.cfg_mngr.getConfigValue(CfgPaths.GENERAL_TEST_INTERVAL_MS.value, 100)
        )

        self.plot_thread.start()

    @QtCore.Slot()
    def stopTest(self):
        self.tare_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.test_timer.stop()
        if self.plot_thread.isRunning():
            self.plot_thread.stopTimer()
        dataframe = self.data_mngr.getDataFrame()
        dataframe_raw = self.data_mngr.getDataFrame(raw_data=True)
        self.test_mngr.testStop()
        print(f"Stopped test: {self.file_mngr.getFileName()}")

        self.file_mngr.saveDataToCSV(dataframe)
        self.file_mngr.saveDataToCSV(dataframe_raw, "_RAW")

        self.start_button.setEnabled(True)
        self.calibration_button.setEnabled(True)
        self.sensors_connect_button.setEnabled(True)

    @QtCore.Slot()
    def tareSensors(self):
        self.stop_button.setEnabled(False)
        self.tare_button.setEnabled(False)

        tare_time_ms = self.cfg_mngr.getConfigValue(
            CfgPaths.GENERAL_TARE_DURATION_MS.value, 3000
        )
        tare_interval_ms = self.cfg_mngr.getConfigValue(
            CfgPaths.GENERAL_TEST_INTERVAL_MS.value, 100
        )

        self.tare_timer.start()
        QtCore.QTimer.singleShot(tare_time_ms, self.tare_timer.stop)

        while self.tare_timer.isActive():
            QtCore.QCoreApplication.processEvents()

        tare_range = tare_time_ms / tare_interval_ms
        if tare_range < 0:
            tare_range = 30

        self.data_mngr.tareSensors(int(tare_range))

        self.stop_button.setEnabled(True)
        self.tare_button.setEnabled(True)

    @QtCore.Slot()
    def calibrateSensors(self):
        self.stacked_widget.setCurrentIndex(1)

    @QtCore.Slot()
    def setConfigFile(self) -> None:
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        config_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Select file", "", "yaml file (*.yaml)", options=options
        )
        if config_file_path:
            self.cfg_mngr.loadConfigFile(config_file_path)
        self.initManagers()
        self.getSensorInformation()
        self.updateTestStatus()

    @QtCore.Slot()
    def setTestFolder(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select folder", options=options
        )
        if folder_path:
            self.file_mngr.setFilePath(folder_path)
            print(f"Changed test folder path to: {folder_path}")
            self.updateTestStatus()

    @QtCore.Slot()
    def setTestName(self):
        test_name = self.test_name_input.text().strip()
        if not test_name:
            test_name = "Test"
        self.file_mngr.setFileName(test_name)
        print(f"Changed test name to: {self.file_mngr.getFileName()}")
        self.updateTestStatus()

    @QtCore.Slot()
    def connectSensors(self):
        self.sensors_connect_button.setEnabled(False)
        self.sensors_connection_progressbar.setValue(50)
        self.test_mngr.checkConnection()
        self.sensors_connection_progressbar.setValue(100)
        self.getSensorInformation()
        self.sensors_connection_progressbar.setValue(0)
        self.updateTestStatus()
        self.sensors_connect_button.setEnabled(True)

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
        pixmap = QtGui.QPixmap(self.logo_img_path)
        image.setPixmap(pixmap)
        image.setAlignment(QtCore.Qt.AlignCenter)
        # Status label
        status_group_box = QtWidgets.QGroupBox("Status Information")
        self.status_vbox_layout = QtWidgets.QVBoxLayout()
        status_group_box.setLayout(self.status_vbox_layout)
        self.status_label = self.createLabelBox(
            "Loading ...", QssLabels.STATUS_LABEL_WARN
        )
        self.status_vbox_layout.addWidget(self.status_label)
        # Buttons
        buttons_group_box = QtWidgets.QGroupBox("Control Panel")
        buttons_vbox_layout = QtWidgets.QVBoxLayout()
        buttons_group_box.setLayout(buttons_vbox_layout)
        self.start_button = self.createQPushButton(
            "Start test", QssLabels.CONTROL_PANEL_BTN, connect_fn=self.startTest
        )
        self.stop_button = self.createQPushButton(
            "Stop test", QssLabels.CONTROL_PANEL_BTN, connect_fn=self.stopTest
        )
        self.tare_button = self.createQPushButton(
            "Tare sensors", QssLabels.CONTROL_PANEL_BTN, connect_fn=self.tareSensors
        )
        self.calibration_button = self.createQPushButton(
            "Calibrate sensors",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=True,
            connect_fn=self.calibrateSensors,
        )
        self.close_button = self.createQPushButton(
            "Close",
            QssLabels.CRITICAL_CONTROL_PANEL_BTN,
            enabled=True,
            connect_fn=self.close_menu.emit,
        )
        buttons_vbox_layout.addWidget(self.start_button)
        buttons_vbox_layout.addWidget(self.tare_button)
        buttons_vbox_layout.addWidget(self.stop_button)
        # Author label
        author_label = self.createLabelBox(
            "© github.AaronPB", QssLabels.AUTHOR_COPYRIGHT_LABEL
        )

        # Build layout
        vbox_layout.addWidget(image)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(status_group_box)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(buttons_group_box)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(self.calibration_button)
        vbox_layout.addItem(
            QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
        )
        vbox_layout.addWidget(self.close_button)
        vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_layout.addWidget(author_label)
        return container

    def loadTabularPanel(self) -> QtWidgets.QTabWidget:
        tabular_panel = QtWidgets.QTabWidget()
        tabular_panel.addTab(self.loadTabSettings(), "Settings and sensor information")
        tabular_panel.addTab(self.loadTabPlatformPlots(), "Platform plots")
        tabular_panel.addTab(self.loadTabCOPPlots(), "COP plots")
        tabular_panel.addTab(self.loadTabEncoderPlots(), "Encoder plots")
        tabular_panel.addTab(self.loadTabIMUPlots(), "IMU plots")
        return tabular_panel

    def loadTabSettings(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        vbox_general_layout = QtWidgets.QVBoxLayout()
        tab_widget.setLayout(vbox_general_layout)
        vbox_general_layout.setAlignment(QtCore.Qt.AlignTop)

        # File management
        settings_group_box = QtWidgets.QGroupBox("File settings")
        settings_grid_layout = QtWidgets.QGridLayout()
        settings_group_box.setLayout(settings_grid_layout)
        settings_grid_layout.setAlignment(QtCore.Qt.AlignTop)
        # - Config file
        config_label = self.createLabelBox("Configuration file:")
        config_button = self.createQPushButton(
            "Select config file", enabled=True, connect_fn=self.setConfigFile
        )
        self.config_path = QtWidgets.QLineEdit(self)
        self.config_path.setReadOnly(True)
        # - Test folder
        test_folder_label = self.createLabelBox("Test folder path:")
        test_folder_button = self.createQPushButton(
            "Select folder", enabled=True, connect_fn=self.setTestFolder
        )
        self.test_folder_path = QtWidgets.QLineEdit(self)
        self.test_folder_path.setReadOnly(True)
        # - Test name
        test_name_label = self.createLabelBox("Test name:")
        test_name_button = self.createQPushButton(
            "Save name", enabled=True, connect_fn=self.setTestName
        )
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
        sensors_group_box = QtWidgets.QGroupBox("Sensor information")
        sensors_vbox_layout = QtWidgets.QVBoxLayout()
        sensors_group_box.setLayout(sensors_vbox_layout)
        sensors_vbox_layout.setAlignment(QtCore.Qt.AlignTop)
        # - Connection button and progress bar
        connect_grid_layout = QtWidgets.QGridLayout()
        self.sensors_connect_button = self.createQPushButton(
            "Connect selected sensors", enabled=True, connect_fn=self.connectSensors
        )
        self.sensors_connection_progressbar = QtWidgets.QProgressBar()
        self.sensors_connection_progressbar.setValue(0)
        connect_grid_layout.addWidget(self.sensors_connect_button, 0, 0)
        connect_grid_layout.addWidget(self.sensors_connection_progressbar, 0, 1)
        # - Sensors grid
        sensors_grid_layout = QtWidgets.QGridLayout()
        group_box_platform1 = QtWidgets.QGroupBox("Platform 1")
        group_box_platform2 = QtWidgets.QGroupBox("Platform 2")
        group_box_external = QtWidgets.QGroupBox("External Sensors")
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

    # TODO WIP
    def loadTabPlatformPlots(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        grid_general_layout = QtWidgets.QGridLayout()
        tab_widget.setLayout(grid_general_layout)

        grid_general_layout.addWidget(self.data_mngr.forces_p1_widget, 0, 0)
        grid_general_layout.addWidget(self.data_mngr.forces_p2_widget, 0, 1)

        return tab_widget

    def loadTabCOPPlots(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        grid_general_layout = QtWidgets.QGridLayout()
        tab_widget.setLayout(grid_general_layout)

        grid_general_layout.addWidget(self.data_mngr.cop_p1_widget, 0, 0)
        grid_general_layout.addWidget(self.data_mngr.cop_p2_widget, 0, 1)

        return tab_widget

    def loadTabEncoderPlots(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        vbox_general_layout = QtWidgets.QVBoxLayout()
        tab_widget.setLayout(vbox_general_layout)

        vbox_general_layout.addWidget(self.data_mngr.encoders_widget)

        return tab_widget

    def loadTabIMUPlots(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        vbox_general_layout = QtWidgets.QVBoxLayout()
        tab_widget.setLayout(vbox_general_layout)

        vbox_general_layout.addWidget(self.data_mngr.imu_angles_widget)

        return tab_widget

    # Functions to load information

    def updateTestStatus(self) -> None:
        status_text = ""
        self.config_path.setText(self.cfg_mngr.getCurrentFilePath())
        self.test_folder_path.setText(self.file_mngr.getFilePath())
        self.test_name_input.setText(self.file_mngr.getFileName())
        if not self.file_mngr.getPathExists():
            status_text = "Invalid test folder!"
        if not self.test_mngr.sensors_connected:
            if status_text != "":
                status_text = status_text + "\n"
            status_text = status_text + "Connect sensors!"

        self.status_label.setParent(None)
        if status_text == "":
            self.status_label = self.createLabelBox(
                "Ready to start test", QssLabels.STATUS_LABEL_OK
            )
            self.status_vbox_layout.addWidget(self.status_label)
            self.setControlPanelButtons(True)
            return
        self.status_label = self.createLabelBox(
            status_text, QssLabels.STATUS_LABEL_WARN
        )
        self.status_vbox_layout.addWidget(self.status_label)
        self.setControlPanelButtons(False)

    def setControlPanelButtons(self, enable: bool = False) -> None:
        if not enable:
            self.stop_button.setEnabled(enable)
            self.tare_button.setEnabled(enable)
        self.start_button.setEnabled(enable)

    def getSensorInformation(self):
        self.setSensorBox(
            self.vbox_platform1,
            self.test_mngr.getP1SensorStatus(),
            self.test_mngr.setP1SensorRead,
        )
        self.setSensorBox(
            self.vbox_platform2,
            self.test_mngr.getP2SensorStatus(),
            self.test_mngr.setP2SensorRead,
        )
        self.setSensorBox(
            self.vbox_external,
            self.test_mngr.getOthersSensorStatus(),
            self.test_mngr.setOthersSensorRead,
        )

    def setSensorBox(
        self, vbox_layout: QtWidgets.QVBoxLayout, sensor_dict: dict, update_fn
    ):
        # Clear layout
        for i in reversed(range(vbox_layout.count())):
            widget = vbox_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        # Add new widgets
        index = 0
        for index, sensor_list in enumerate(sensor_dict.values()):
            checkbox = self.createSensorQCheckBox(
                sensor_list[0] + " (" + sensor_list[1] + ")",
                sensor_list[2].value,
                change_fn=update_fn,
                index=index,
            )
            checkbox.setChecked(sensor_list[3])
            vbox_layout.addWidget(checkbox)
