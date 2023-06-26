# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import os
import time

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from PyQt5 import QtWidgets, QtGui, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from src.inputReader import InputReader
from src.interfaceCalibration import MainCalibrationMenu
from src.utils import LogHandler


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.log_handler = LogHandler(str(__class__.__name__))
        self.dir_images = os.path.join(
            os.path.dirname(__file__), '..', 'images')
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Force platform reader')
        self.setWindowIcon(QtGui.QIcon(
            os.path.join(self.dir_images, 'logo.ico')))
        screen_resolution = QtWidgets. QDesktopWidget().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.setGeometry(width//4, height//4,
                         int(width//1.5), int(height//1.12))

        # Main GUI layouts
        self.interface = QtWidgets.QWidget(self)
        self.interface_box = QtWidgets.QHBoxLayout()
        hbox_main = QtWidgets.QVBoxLayout()
        self.hbox_top = QtWidgets.QHBoxLayout()
        self.hbox_mid = QtWidgets.QHBoxLayout()
        self.hbox_bottom = QtWidgets.QHBoxLayout()

        # Spacers
        spacer_20 = QtWidgets.QSpacerItem(
            20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)

        # Inner layouts adjustments
        self.hbox_top.setAlignment(QtCore.Qt.AlignTop)
        self.hbox_mid.setAlignment(QtCore.Qt.AlignTop)
        self.hbox_bottom.setAlignment(QtCore.Qt.AlignBottom)

        # Build
        hbox_main.setAlignment(QtCore.Qt.AlignTop)
        hbox_main.addLayout(self.hbox_top)
        hbox_main.addItem(spacer_20)
        hbox_main.addLayout(self.hbox_mid)
        hbox_main.addItem(spacer_20)
        hbox_main.addLayout(self.hbox_bottom)

        self.interface_box.addWidget(self.interface)
        self.interface.setLayout(hbox_main)
        self.setLayout(self.interface_box)

        # Load reader software and timers
        self.inputReader = InputReader()
        self.test_timer = QtCore.QTimer(self)
        self.test_timer.timeout.connect(self.inputReader.readerProcess)
        self.tare_timer = QtCore.QTimer(self)

        # Load layouts
        self.loadIconLayout()
        self.hbox_top.addItem(spacer_20)
        self.loadFilesLayout()

        self.loadPanelLayout()
        self.hbox_mid.addItem(spacer_20)
        self.loadSensorLayout()

        self.updatePaths()
        self.updateTestChecks()

        # Load calibration menu and hide it
        self.calibration_menu = MainCalibrationMenu(self, self.inputReader)
        self.interface_box.addWidget(self.calibration_menu)
        self.calibration_menu.hide()

        # Load default plots
        self.generatePlots()

        self.show()

    # TOP LAYOUT METHODS
    def loadIconLayout(self):
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)

        image = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap(os.path.join(self.dir_images, 'logo.ico'))
        image.setPixmap(pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio))
        image.setAlignment(QtCore.Qt.AlignCenter)
        label = QtWidgets.QLabel('Force Platform Reader', self)
        label.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        label.setAlignment(QtCore.Qt.AlignCenter)

        vbox_layout.addWidget(image)
        vbox_layout.addWidget(label)
        self.hbox_top.addLayout(vbox_layout)

    def loadFilesLayout(self):
        vbox_layout = QtWidgets.QGridLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)

        # Config file
        config_label = QtWidgets.QLabel('Configuration file:', self)
        config_btn = QtWidgets.QPushButton('Select config file', self)
        config_btn.clicked.connect(self.selectFile)
        self.config_path = QtWidgets.QLineEdit(self)
        self.config_path.setReadOnly(True)

        # Test folder
        test_path_label = QtWidgets.QLabel('Test folder path:', self)
        test_path_btn = QtWidgets.QPushButton('Select folder path', self)
        test_path_btn.clicked.connect(self.selectFolder)
        self.test_path = QtWidgets.QLineEdit(self)
        self.test_path.setReadOnly(True)

        # Test name
        text_label = QtWidgets.QLabel('Test name:', self)
        self.text_input = QtWidgets.QLineEdit(self)
        aplicar_btn = QtWidgets.QPushButton('Set file name', self)
        aplicar_btn.clicked.connect(self.applyText)

        vbox_layout.addWidget(config_label, 0, 0)
        vbox_layout.addWidget(self.config_path, 0, 1)
        vbox_layout.addWidget(config_btn, 0, 2)
        vbox_layout.addWidget(test_path_label, 1, 0)
        vbox_layout.addWidget(self.test_path, 1, 1)
        vbox_layout.addWidget(test_path_btn, 1, 2)
        vbox_layout.addWidget(text_label, 2, 0)
        vbox_layout.addWidget(self.text_input, 2, 1)
        vbox_layout.addWidget(aplicar_btn, 2, 2)
        self.hbox_top.addLayout(vbox_layout)

    def updatePaths(self):
        self.config_path.setText(self.inputReader.config_path)
        self.test_path.setText(self.inputReader.test_folder)
        self.text_input.setText(self.inputReader.test_name)

    def selectFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        config_file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Select file', '', 'Archivo yaml (*.yaml)', options=options)
        if config_file_path:
            self.config_path.setText(config_file_path)
            self.inputReader.configLoadCustomFile(config_file_path)
            self.updateSensorPanel()

    def selectFolder(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Select folder', options=options)
        if folder_path:
            self.inputReader.configEdit(
                'general_settings.test_file_path.folder', folder_path)
            self.inputReader.loadGeneralSettings()
            self.updatePaths()
            self.log_handler.logger.info(
                "Changed folder path to: " + str(folder_path))
            self.updateTestChecks()

    def applyText(self):
        name = self.text_input.text().strip()
        if not name:
            name = "Test"
        self.inputReader.configEdit(
            'general_settings.test_file_path.name', name)
        self.inputReader.loadGeneralSettings()
        self.updatePaths()
        self.log_handler.logger.info("Changed test name to: " + str(name))
        self.updateTestChecks()

    # MID LAYOUT METHODS
    def loadPanelLayout(self):
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)
        title = QtWidgets.QLabel("Control panel")
        title.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)

        self.calibrate_sensors_btn = QtWidgets.QPushButton(
            'Calibrate sensors', self)
        self.calibrate_sensors_btn.setEnabled(False)
        self.calibrate_sensors_btn.clicked.connect(self.openCalibrationMenu)
        self.start_btn = QtWidgets.QPushButton('Start test', self)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.startTest)
        self.tare_btn = QtWidgets.QPushButton('Tare sensors', self)
        self.tare_btn.setEnabled(False)
        self.tare_btn.clicked.connect(self.tareSensors)
        self.vbox_test_check = QtWidgets.QVBoxLayout()
        self.stop_btn = QtWidgets.QPushButton('Stop test', self)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stopTest)
        close_btn = QtWidgets.QPushButton('Close menu', self)
        close_btn.clicked.connect(self.close)

        vbox_layout.addWidget(title)
        vbox_layout.addWidget(self.calibrate_sensors_btn)
        vbox_layout.addWidget(self.start_btn)
        vbox_layout.addWidget(self.tare_btn)
        vbox_layout.addLayout(self.vbox_test_check)
        vbox_layout.addWidget(self.stop_btn)
        vbox_layout.addWidget(close_btn)
        self.hbox_mid.addLayout(vbox_layout)

    def loadSensorLayout(self):
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)

        # First layout with title and sensor update button
        hbox_title_layout = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Sensor information")
        title.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)

        update_sensors_btn = QtWidgets.QPushButton(
            'Connect sensors', self)
        update_sensors_btn.setMaximumWidth(200)
        update_sensors_btn.clicked.connect(self.connectSensors)

        hbox_title_layout.addWidget(update_sensors_btn)
        hbox_title_layout.addWidget(title)

        # Sensor grid
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)
        grid_layout.setAlignment(QtCore.Qt.AlignTop)

        vbox_p1 = QtWidgets.QVBoxLayout()
        vbox_p1.addWidget(QtWidgets.QLabel("Platform 1"))
        vbox_p2 = QtWidgets.QVBoxLayout()
        vbox_p2.addWidget(QtWidgets.QLabel("Platform 2"))
        vbox_p3 = QtWidgets.QVBoxLayout()
        vbox_p3.addWidget(QtWidgets.QLabel("External sensors"))
        grid_layout.addLayout(vbox_p1, 0, 0)
        grid_layout.addLayout(vbox_p2, 0, 1)
        grid_layout.addLayout(vbox_p3, 0, 2)

        # Sensor information
        vbox_p1.addLayout(self.loadSensorGridLayout(
            self.inputReader.getPlatform1SensorStatus()))
        vbox_p2.addLayout(self.loadSensorGridLayout(
            self.inputReader.getPlatform2SensorStatus()))
        vbox_p3.addLayout(self.loadSensorGridLayout(
            self.inputReader.getEncoderSensorsStatus()))
        vbox_p3.addLayout(self.loadSensorGridLayout(
            self.inputReader.getIMUSensorStatus()))

        vbox_layout.addLayout(hbox_title_layout)
        vbox_layout.addLayout(grid_layout)
        self.hbox_mid.addLayout(vbox_layout)

    def updateSensorPanel(self):
        # Clear grid layouts and load again
        sensor_layout = self.hbox_mid.itemAt(2).layout()
        if sensor_layout is not None:
            hbox = sensor_layout.itemAt(0).layout()
            grid = sensor_layout.itemAt(1).layout()
            while hbox.count():
                item = hbox.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            for i in reversed(range(grid.count())):
                grid_vbox_layout = grid.itemAt(i)
                if grid_vbox_layout.layout is not None:
                    while grid_vbox_layout.count():
                        element = grid_vbox_layout.takeAt(0)
                        if element.widget() is not None:
                            element.widget().deleteLater()
                        elif element.layout() is not None and isinstance(element, QtWidgets.QGridLayout):
                            for i in range(element.rowCount()):
                                for j in range(element.columnCount()):
                                    widget = element.itemAtPosition(
                                        i, j).widget()
                                    if widget is not None:
                                        widget.deleteLater()
                    grid.removeItem(grid_vbox_layout)
            sensor_layout.removeItem(hbox)
            sensor_layout.removeItem(grid)
            hbox.deleteLater()
            grid.deleteLater()
            self.hbox_mid.removeItem(sensor_layout)

        self.updateTestChecks()
        self.loadSensorLayout()
        self.update()

    def loadSensorGridLayout(self, status_list):
        loadcell_layout = QtWidgets.QGridLayout()
        loadcell_layout.setColumnStretch(0, 0)
        loadcell_layout.setColumnStretch(1, 0)
        loadcell_layout.setColumnStretch(2, 1)
        loadcell_layout.setColumnMinimumWidth(0, 25)
        loadcell_layout.setColumnMinimumWidth(1, 20)
        loadcell_layout.setHorizontalSpacing(5)
        loadcell_layout.setVerticalSpacing(5)
        loadcell_layout.setAlignment(QtCore.Qt.AlignLeft)

        for i, sensor in enumerate(status_list):
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(sensor['read_data'])
            checkbox.setObjectName(sensor['config_path'])
            checkbox.stateChanged.connect(self.handleSensorCheckbox)
            loadcell_layout.addWidget(checkbox, i, 0)

            label = QtWidgets.QLabel()
            label.setStyleSheet('background-color: grey')
            if sensor['status'] == 'Disconnected':
                label.setStyleSheet('background-color: red')
            elif sensor['status'] == 'Active':
                label.setStyleSheet('background-color: green')
            loadcell_layout.addWidget(label, i, 1)

            label = QtWidgets.QLabel(sensor['name'])
            loadcell_layout.addWidget(label, i, 2)
        return loadcell_layout

    def handleSensorCheckbox(self, state):
        sender = self.sender()
        self.inputReader.configEdit(
            sender.objectName() + '.read_data', state == 2)

    def connectSensors(self):
        self.inputReader.connectSensors()
        self.updateSensorPanel()

    def updateTestChecks(self):
        test_status_text = [
            ('Config loaded', '(!!) Pending config upload'),
            ('Folder path selected', '(!!) Select a folder to save files'),
            ('Test name set', '(!!) Set a test name'),
            ('Sensors connected', '(!!) Connect at least one sensor')]
        test_status = self.inputReader.getReaderChecks()

        while self.vbox_test_check.count():
            child = self.vbox_test_check.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        test_available = True
        for i, ok in enumerate(test_status):
            output = test_status_text[i][0] if ok else test_status_text[i][1]
            label = QtWidgets.QLabel(output)
            label.setMinimumSize(20, 20)
            label.setStyleSheet("color: green;")
            if not ok:
                label.setStyleSheet("color: red;")
                test_available = False
            self.vbox_test_check.addWidget(label)

        self.start_btn.setEnabled(test_available)
        self.calibrate_sensors_btn.setEnabled(test_available)

    def startTest(self):
        self.start_btn.setEnabled(False)
        self.calibrate_sensors_btn.setEnabled(False)
        self.inputReader.readerStart()
        self.tare_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        # Start reader process with the specified rate in ms
        self.test_timer.start(self.inputReader.getTestInterval())

    def stopTest(self):
        self.tare_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.test_timer.stop()
        self.inputReader.readerStop()
        self.start_btn.setEnabled(True)
        self.calibrate_sensors_btn.setEnabled(True)
        self.updatePlots()

    def tareSensors(self):
        self.stop_btn.setEnabled(False)
        self.tare_btn.setEnabled(False)
        start_time = round(time.time()*1000)
        self.tare_timer.start()
        # Tare with current data in specified time
        QtCore.QTimer.singleShot(
            self.inputReader.getTestTareTime(), self.tare_timer.stop)

        while self.tare_timer.isActive():
            QtCore.QCoreApplication.processEvents()

        end_time = round(time.time()*1000)
        self.inputReader.tareApply(start_time, end_time)
        self.tare_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

    def openCalibrationMenu(self):
        self.interface.hide()
        self.calibration_menu.updateGridLayout()
        self.calibration_menu.show()

    # BOTTOM LAYOUT METHODS
    def generatePlots(self):
        vbox_plot1 = QtWidgets.QVBoxLayout()
        vbox_plot2 = QtWidgets.QVBoxLayout()
        vbox_plot3 = QtWidgets.QVBoxLayout()

        # Plot titles
        title_plot1 = QtWidgets.QLabel("Platform 1 COP")
        title_plot1.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        title_plot1.setAlignment(QtCore.Qt.AlignCenter)
        title_plot2 = QtWidgets.QLabel("Platform 2 COP")
        title_plot2.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        title_plot2.setAlignment(QtCore.Qt.AlignCenter)
        title_plot3 = QtWidgets.QLabel("IMU values")
        title_plot3.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        title_plot3.setAlignment(QtCore.Qt.AlignCenter)

        # Rectangle side lenghts
        x_length = 600  # mm
        y_length = 400  # mm
        rect1 = patches.Rectangle(
            (-x_length/2, -y_length/2), x_length, y_length, edgecolor='blue', facecolor='none')
        rect2 = patches.Rectangle(
            (-x_length/2, -y_length/2), x_length, y_length, edgecolor='blue', facecolor='none')

        # Generate empty plots
        self.fig1, self.ax1 = plt.subplots()
        self.canvas1 = FigureCanvas(self.fig1)
        self.ax1.set_xlabel('Medio-Lateral Motion (mm)')
        self.ax1.set_ylabel('Anterior-Posterior Motion (mm)')
        toolbar1 = NavigationToolbar(self.canvas1, self)
        self.line1, = self.ax1.plot(0, 0)
        self.ax1.grid(True)
        self.ax1.add_patch(rect1)

        self.fig2, self.ax2 = plt.subplots()
        self.canvas2 = FigureCanvas(self.fig2)
        toolbar2 = NavigationToolbar(self.canvas2, self)
        self.ax2.set_xlabel('Medio-Lateral Motion (mm)')
        self.ax2.set_ylabel('Anterior-Posterior Motion (mm)')
        self.line2, = self.ax2.plot(0, 0)
        self.ax2.grid(True)
        self.ax2.add_patch(rect2)

        self.fig3, self.ax3 = plt.subplots()
        self.canvas3 = FigureCanvas(self.fig3)
        toolbar3 = NavigationToolbar(self.canvas3, self)
        self.ax3.set_xlabel('Time (s)')
        self.ax3.set_ylabel('Absolute reference angle (rad)')
        self.ax3.plot(0, 0)
        self.ax3.grid(True)

        # Layouts
        vbox_plot1.addWidget(title_plot1)
        vbox_plot1.addWidget(toolbar1)
        vbox_plot1.addWidget(self.canvas1)
        vbox_plot2.addWidget(title_plot2)
        vbox_plot2.addWidget(toolbar2)
        vbox_plot2.addWidget(self.canvas2)
        vbox_plot3.addWidget(title_plot3)
        vbox_plot3.addWidget(toolbar3)
        vbox_plot3.addWidget(self.canvas3)

        self.hbox_bottom.addLayout(vbox_plot1)
        self.hbox_bottom.addLayout(vbox_plot2)
        self.hbox_bottom.addLayout(vbox_plot3)

    def updatePlots(self):
        x_cop_p1, y_cop_p1, x_cop_p2, y_cop_p2, \
            ankle_angle, thigh_angle, trunk_angle = \
            self.inputReader.getPlotterData()
        # Update relative COP Platform 1
        self.line1.set_data(x_cop_p1, y_cop_p1)
        self.canvas1.draw()
        # Update relative COP Platform 2
        self.line2.set_data(x_cop_p2, y_cop_p2)
        self.canvas2.draw()
        # TODO Update IMU
