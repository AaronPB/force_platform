# -*- coding: utf-8 -*-

from src.enums.qssLabels import QssLabels
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.uiResources import IconPaths, ImagePaths
from src.managers.configManager import ConfigManager
from src.managers.testManager import TestManager
from src.managers.fileManager import FileManager
from src.managers.dataManager import DataManager
from src.managers.sensorManager import SensorManager
from src.qtUIs.widgets import customQtLoaders as customQT
from src.qtUIs.widgets.mainWidgets import SensorSettings, SensorPlotSelector
from PySide6 import QtWidgets, QtGui, QtCore


class MainUI(QtWidgets.QWidget):
    close_menu = QtCore.Signal()

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

        self.test_mngr = TestManager()
        self.data_mngr = DataManager()

        self.initManagers()
        self.initUI()
        self.updateTestStatus()
        self.getSensorInformation()

    def initManagers(self) -> None:
        self.file_mngr = FileManager(self.cfg_mngr)
        self.sensor_mngr.setup()
        self.test_mngr.setSensorGroups(self.sensor_mngr.getGroups())
        # TODO data_mngr

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

    # UI buttons click connectors

    @QtCore.Slot()
    def startTest(self):
        # Update file name in case
        self.file_mngr.checkFileName()
        self.test_name_input.setText(self.file_mngr.getFileName())

        self.start_button.setEnabled(False)
        self.sensors_connect_button.setEnabled(False)
        self.update_results_button.setEnabled(False)
        self.calibration_button.setEnabled(False)
        self.test_mngr.testStart(self.file_mngr.getFileName())
        self.tare_button.setEnabled(True)
        self.stop_button.setEnabled(True)

        self.test_timer.start(
            self.cfg_mngr.getConfigValue(CfgPaths.RECORD_INTERVAL_MS.value, 100)
        )

    @QtCore.Slot()
    def stopTest(self):
        self.tare_button.setEnabled(False)
        self.stop_button.setEnabled(False)

        # Stop test
        self.test_timer.stop()
        self.test_mngr.testStop(self.file_mngr.getFileName())

        # Get results from recorded data
        self.data_mngr.loadData(
            self.test_mngr.getTestTimes(), self.sensor_mngr.getGroups()
        )
        self.loadResults()
        dataframe = self.data_mngr.getCalibrateDataframe()
        dataframe_raw = self.data_mngr.getRawDataframe()

        # Update plot options and data settings
        self.sensor_plotter.updateLayouts()
        self.setDataSettings(True)

        # Save dataframes
        if self.cfg_mngr.getConfigValue(CfgPaths.TEST_SAVE_CALIB.value, True):
            self.file_mngr.saveDataToCSV(dataframe)
        if self.cfg_mngr.getConfigValue(CfgPaths.TEST_SAVE_RAW.value, True):
            self.file_mngr.saveDataToCSV(dataframe_raw, "_RAW")

        self.start_button.setEnabled(True)
        self.calibration_button.setEnabled(True)
        self.sensors_connect_button.setEnabled(True)
        self.update_results_button.setEnabled(True)

    @QtCore.Slot()
    def tareSensors(self):
        self.stop_button.setEnabled(False)
        self.tare_button.setEnabled(False)

        tare_amount = self.cfg_mngr.getConfigValue(
            CfgPaths.RECORD_TARE_AMOUNT.value, 300
        )
        tare_interval_ms = self.cfg_mngr.getConfigValue(
            CfgPaths.RECORD_INTERVAL_MS.value, 100
        )
        tare_time_ms = int(tare_amount * tare_interval_ms)

        self.tare_timer.start()
        QtCore.QTimer.singleShot(tare_time_ms, self.tare_timer.stop)

        while self.tare_timer.isActive():
            QtCore.QCoreApplication.processEvents()

        self.data_mngr.tareSensors(self.sensor_mngr, tare_amount)

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
        # self.updatePlotTabs()
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
            self.updateTestStatus()

    @QtCore.Slot()
    def setTestName(self):
        test_name = self.test_name_input.text().strip()
        if not test_name:
            test_name = "Test"
        self.file_mngr.setFileName(test_name)
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

    # - Control Panel

    def loadControlPanelContainer(self) -> QtWidgets.QWidget:
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)
        # Container to fix width of control panel
        container = QtWidgets.QWidget()
        container.setLayout(vbox_layout)
        container.setFixedWidth(250)
        # Top icon
        image = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(ImagePaths.LOGO.value)
        image.setPixmap(pixmap)
        image.setAlignment(QtCore.Qt.AlignCenter)
        # Status label
        status_group_box = QtWidgets.QGroupBox("Status Information")
        self.status_vbox_layout = QtWidgets.QVBoxLayout()
        status_group_box.setLayout(self.status_vbox_layout)
        self.status_label = customQT.createLabelBox(
            "Loading ...", QssLabels.STATUS_LABEL_WARN
        )
        self.status_vbox_layout.addWidget(self.status_label)
        # Buttons
        buttons_group_box = QtWidgets.QGroupBox("Control Panel")
        buttons_vbox_layout = QtWidgets.QVBoxLayout()
        buttons_group_box.setLayout(buttons_vbox_layout)
        self.start_button = customQT.createQPushButton(
            " Start test",
            QssLabels.CONTROL_PANEL_BTN,
            icon_path=IconPaths.SEND,
            connect_fn=self.startTest,
        )
        self.stop_button = customQT.createQPushButton(
            "Stop test", QssLabels.CONTROL_PANEL_BTN, connect_fn=self.stopTest
        )
        self.tare_button = customQT.createQPushButton(
            "Tare sensors", QssLabels.CONTROL_PANEL_BTN, connect_fn=self.tareSensors
        )
        self.calibration_button = customQT.createQPushButton(
            "Calibrate sensors",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=True,
            connect_fn=self.calibrateSensors,
        )
        self.close_button = customQT.createQPushButton(
            "Close",
            QssLabels.CRITICAL_CONTROL_PANEL_BTN,
            enabled=True,
            connect_fn=self.close_menu.emit,
        )
        buttons_vbox_layout.addWidget(self.start_button)
        buttons_vbox_layout.addWidget(self.tare_button)
        buttons_vbox_layout.addWidget(self.stop_button)
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
        vbox_layout.addLayout(credits_layout)
        return container

    # - Tab Widget

    def loadTabularPanel(self) -> QtWidgets.QTabWidget:
        tabular_panel = QtWidgets.QTabWidget()
        tabular_panel.addTab(
            self.loadTabSettings(), QtGui.QIcon(IconPaths.SETTINGS.value), "Settings"
        )
        tabular_panel.addTab(
            self.loadTabFigures(), QtGui.QIcon(IconPaths.GRAPH.value), "Figures"
        )
        return tabular_panel

    def loadTabSettings(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        vbox_general_layout = QtWidgets.QVBoxLayout()
        tab_widget.setLayout(vbox_general_layout)
        vbox_general_layout.setAlignment(QtCore.Qt.AlignTop)

        # File management
        file_settings_group_box = QtWidgets.QGroupBox("File settings")
        file_settings_grid_layout = QtWidgets.QGridLayout()
        file_settings_group_box.setLayout(file_settings_grid_layout)
        file_settings_grid_layout.setAlignment(QtCore.Qt.AlignTop)
        # - Config file
        config_label = customQT.createLabelBox("Configuration file:")
        config_button = customQT.createQPushButton(
            "Select config file", enabled=True, connect_fn=self.setConfigFile
        )
        self.config_path = QtWidgets.QLineEdit(self)
        self.config_path.setReadOnly(True)
        # - Test folder
        test_folder_label = customQT.createLabelBox("Test folder path:")
        test_folder_button = customQT.createQPushButton(
            "Select folder", enabled=True, connect_fn=self.setTestFolder
        )
        self.test_folder_path = QtWidgets.QLineEdit(self)
        self.test_folder_path.setReadOnly(True)
        # - Test name
        test_name_label = customQT.createLabelBox("Test name:")
        test_name_button = customQT.createQPushButton(
            "Save name", enabled=True, connect_fn=self.setTestName
        )
        self.test_name_input = QtWidgets.QLineEdit(self)
        # - Build grid layout
        file_settings_grid_layout.addWidget(config_label, 0, 0)
        file_settings_grid_layout.addWidget(self.config_path, 0, 1)
        file_settings_grid_layout.addWidget(config_button, 0, 2)
        file_settings_grid_layout.addWidget(test_folder_label, 1, 0)
        file_settings_grid_layout.addWidget(self.test_folder_path, 1, 1)
        file_settings_grid_layout.addWidget(test_folder_button, 1, 2)
        file_settings_grid_layout.addWidget(test_name_label, 2, 0)
        file_settings_grid_layout.addWidget(self.test_name_input, 2, 1)
        file_settings_grid_layout.addWidget(test_name_button, 2, 2)

        # TODO WIP Results data settings
        data_settings_group_box = QtWidgets.QGroupBox("Results settings")
        data_settings_layout = QtWidgets.QHBoxLayout()
        data_settings_group_box.setLayout(data_settings_layout)
        data_settings_layout.setAlignment(QtCore.Qt.AlignTop)

        # - Data start and end points
        data_index_header = customQT.createLabelBox("Modify data range:")
        data_index_grid = QtWidgets.QGridLayout()
        self.data_start = QtWidgets.QSpinBox()
        self.data_end = QtWidgets.QSpinBox()
        self.setDataSettings(False)
        data_index_grid.addWidget(QtWidgets.QLabel("First index:"), 0, 0)
        data_index_grid.addWidget(self.data_start, 0, 1)
        data_index_grid.addWidget(QtWidgets.QLabel("Last index:"), 1, 0)
        data_index_grid.addWidget(self.data_end, 1, 1)

        # - Butterworth filter options
        filter_header = customQT.createLabelBox("Modify Butterworth filter:")
        filter_grid = QtWidgets.QGridLayout()
        self.filter_fs_input = QtWidgets.QSpinBox()
        self.filter_fs_input.setMaximum(200)
        self.filter_fs_input.setValue(100)
        self.filter_fc_input = QtWidgets.QSpinBox()
        self.filter_fc_input.setMaximum(10)
        self.filter_fc_input.setValue(5)
        self.filter_order_input = QtWidgets.QSpinBox()
        self.filter_order_input.setMaximum(10)
        self.filter_order_input.setValue(6)
        filter_grid.addWidget(QtWidgets.QLabel("Sampling rate (Fs):"), 0, 0)
        filter_grid.addWidget(self.filter_fs_input, 0, 1)
        filter_grid.addWidget(QtWidgets.QLabel("Hz"), 0, 2)
        filter_grid.addWidget(QtWidgets.QLabel("Cutoff freq (Fc):"), 1, 0)
        filter_grid.addWidget(self.filter_fc_input, 1, 1)
        filter_grid.addWidget(QtWidgets.QLabel("Hz"), 1, 2)
        filter_grid.addWidget(QtWidgets.QLabel("Order:"), 2, 0)
        filter_grid.addWidget(self.filter_order_input, 2, 1)

        # - Recalculate button
        self.update_results_button = customQT.createQPushButton(
            "Apply changes",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=False,
            connect_fn=self.loadResults,
        )

        # - Data preview
        self.data_settings_preview = QtWidgets.QVBoxLayout()
        self.data_settings_preview.addWidget(
            customQT.createLabelBox("", QssLabels.PREVIEW_BOX)
        )

        # -  Build layout
        data_options_container = QtWidgets.QWidget()
        data_options_layout = QtWidgets.QVBoxLayout()
        data_options_container.setLayout(data_options_layout)
        data_options_container.setFixedWidth(400)
        data_options_layout.setAlignment(QtCore.Qt.AlignTop)
        data_options_layout.addWidget(data_index_header)
        data_options_layout.addLayout(data_index_grid)
        data_options_layout.addItem(QtWidgets.QSpacerItem(10, 10))
        data_options_layout.addWidget(filter_header)
        data_options_layout.addLayout(filter_grid)
        data_options_layout.addItem(QtWidgets.QSpacerItem(10, 10))
        data_options_layout.addWidget(self.update_results_button)

        data_settings_layout.addWidget(data_options_container)
        data_settings_layout.addLayout(self.data_settings_preview)

        # Sensor table information
        sensors_group_box = QtWidgets.QGroupBox("Sensor information")
        sensors_vbox_layout = QtWidgets.QVBoxLayout()
        sensors_group_box.setLayout(sensors_vbox_layout)
        sensors_vbox_layout.setAlignment(QtCore.Qt.AlignTop)
        # - Connection button and progress bar
        connect_grid_layout = QtWidgets.QGridLayout()
        self.sensors_connect_button = customQT.createQPushButton(
            "Connect selected sensors", enabled=True, connect_fn=self.connectSensors
        )
        self.sensors_connection_progressbar = QtWidgets.QProgressBar()
        self.sensors_connection_progressbar.setValue(0)
        connect_grid_layout.addWidget(self.sensors_connect_button, 0, 0)
        connect_grid_layout.addWidget(self.sensors_connection_progressbar, 0, 1)
        # - Sensors grid
        sensors_layout = QtWidgets.QVBoxLayout()
        group_box_platforms = QtWidgets.QGroupBox("Platforms")
        group_box_defaults = QtWidgets.QGroupBox("Other sensor groups")
        self.hbox_platforms = QtWidgets.QHBoxLayout()
        self.hbox_defaults = QtWidgets.QHBoxLayout()
        self.hbox_platforms.setAlignment(QtCore.Qt.AlignTop)
        self.hbox_defaults.setAlignment(QtCore.Qt.AlignTop)
        group_box_platforms.setLayout(self.hbox_platforms)
        group_box_defaults.setLayout(self.hbox_defaults)
        sensors_layout.addWidget(group_box_platforms)
        sensors_layout.addWidget(group_box_defaults)
        # Build sensor information layout
        sensors_vbox_layout.addLayout(connect_grid_layout)
        sensors_vbox_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        sensors_vbox_layout.addLayout(sensors_layout)

        # Build main tab vbox
        vbox_general_layout.addWidget(file_settings_group_box)
        vbox_general_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_general_layout.addWidget(data_settings_group_box)
        vbox_general_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_general_layout.addWidget(sensors_group_box)

        return tab_widget

    def loadTabFigures(self) -> QtWidgets.QWidget:
        tab_widget = QtWidgets.QWidget()
        vbox_general_layout = QtWidgets.QVBoxLayout()
        tab_widget.setLayout(vbox_general_layout)
        vbox_general_layout.setAlignment(QtCore.Qt.AlignTop)

        # Top sensor selector
        selector_box = QtWidgets.QGroupBox("Sensor selector")
        selector_layout = QtWidgets.QHBoxLayout()
        selector_box.setLayout(selector_layout)

        group_box_sensor_groups = QtWidgets.QGroupBox("Select group")
        group_box_sensors = QtWidgets.QGroupBox("Select sensor")
        group_box_options = QtWidgets.QGroupBox("Select option")
        self.vbox_selector_groups = QtWidgets.QVBoxLayout()
        self.vbox_selector_sensors = QtWidgets.QVBoxLayout()
        self.vbox_selector_options = QtWidgets.QVBoxLayout()
        self.vbox_selector_groups.setAlignment(QtCore.Qt.AlignTop)
        self.vbox_selector_sensors.setAlignment(QtCore.Qt.AlignTop)
        self.vbox_selector_options.setAlignment(QtCore.Qt.AlignTop)
        group_box_sensor_groups.setLayout(self.vbox_selector_groups)
        group_box_sensors.setLayout(self.vbox_selector_sensors)
        group_box_options.setLayout(self.vbox_selector_options)
        selector_layout.addWidget(group_box_sensor_groups)
        selector_layout.addWidget(group_box_sensors)
        selector_layout.addWidget(group_box_options)

        # Figure layout
        figure_box = QtWidgets.QGroupBox("Figure")
        self.figure_layout = QtWidgets.QVBoxLayout()
        figure_box.setLayout(self.figure_layout)
        self.figure_layout.addWidget(
            customQT.createLabelBox(
                "First preform a test and select a plot option from the sensor selector panel",
                QssLabels.STATUS_LABEL_WARN,
            )
        )

        # Build general layout
        vbox_general_layout.addWidget(selector_box)
        vbox_general_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        vbox_general_layout.addWidget(figure_box)

        # Define selector class
        self.sensor_plotter = SensorPlotSelector(self.sensor_mngr, self.data_mngr)
        self.sensor_plotter.setupLayouts(
            self.vbox_selector_groups,
            self.vbox_selector_sensors,
            self.vbox_selector_options,
            self.figure_layout,
        )

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
            self.status_label = customQT.createLabelBox(
                "Ready to start test", QssLabels.STATUS_LABEL_OK
            )
            self.status_vbox_layout.addWidget(self.status_label)
            self.setControlPanelButtons(True)
            return
        self.status_label = customQT.createLabelBox(
            status_text, QssLabels.STATUS_LABEL_WARN
        )
        self.status_vbox_layout.addWidget(self.status_label)
        self.setControlPanelButtons(False)

    def setControlPanelButtons(self, enable: bool = False) -> None:
        if not enable:
            self.stop_button.setEnabled(enable)
            self.tare_button.setEnabled(enable)
        self.start_button.setEnabled(enable)

    def setDataSettings(self, enable: bool = False) -> None:
        self.data_start.setValue(0)
        self.data_end.setValue(0)
        if enable:
            max_value = self.data_mngr.getDataSize()
            self.data_start.setMinimum(0)
            self.data_start.setMaximum(max_value - 1)
            self.data_end.setMinimum(1)
            self.data_end.setMaximum(max_value)
            self.data_end.setValue(max_value)
        self.data_start.setEnabled(enable)
        self.data_end.setEnabled(enable)

    def getSensorInformation(self):
        sensor_panels = SensorSettings(self.sensor_mngr)
        sensor_panels.updateLayout(
            self.hbox_platforms, self.sensor_mngr.getPlatformGroups()
        )
        sensor_panels.updateLayout(
            self.hbox_defaults, self.sensor_mngr.getDefaultGroups()
        )

    def loadResults(self):
        idx1 = self.data_start.value()
        idx2 = self.data_end.value()
        self.sensor_plotter.setIndexes(idx1, idx2)
        butter_fs = self.filter_fs_input.value()
        butter_fc = self.filter_fc_input.value()
        butter_order = self.filter_order_input.value()
        self.data_mngr.applyButterFilter(butter_fs, butter_fc, butter_order)
