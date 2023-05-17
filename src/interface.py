# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import os
# import numpy as np
# import matplotlib.pyplot as plt

from PyQt5 import QtWidgets, QtGui, QtCore
# from PyQt5.QtGui import QPixmap, QIcon, QFont
# from PyQt5.QtCore import Qt, QTimer
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from src.inputReader import InputReader
from src.interfaceCalibration import MainCalibrationMenu
from src.utils import LogHandler


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.log_handler = LogHandler(str(__class__.__name__))
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Programa de lecturas')
        self.setWindowIcon(QtGui.QIcon('logo.ico'))
        screen_resolution = QtWidgets. QDesktopWidget().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.setGeometry(width//4, height//4, width//2, height//2)

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

        # Load reader software and test timer
        self.inputReader = InputReader()
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.inputReader.readerProcess)

        # Load layouts
        self.loadIconLayout()
        self.hbox_top.addItem(spacer_20)
        self.loadFilesLayout()

        self.loadPanelLayout()
        self.hbox_mid.addItem(spacer_20)
        self.loadSensorLayout()

        self.updatePaths()
        self.updateTestChecks()

        # Load default plots
        # self.generateExamplePlots()

        self.show()

    # TOP LAYOUT METHODS
    def loadIconLayout(self):
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)

        image = QtWidgets.QLabel(self)
        pixmap = QtGui.QPixmap('logo.ico')
        image.setPixmap(pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio))
        image.setAlignment(QtCore.Qt.AlignCenter)
        label = QtWidgets.QLabel('Plataforma fuerza', self)
        label.setFont(QtGui.QFont("Arial", 12, QtGui.QFont.Bold))
        label.setAlignment(QtCore.Qt.AlignCenter)

        vbox_layout.addWidget(image)
        vbox_layout.addWidget(label)
        self.hbox_top.addLayout(vbox_layout)

    def loadFilesLayout(self):
        vbox_layout = QtWidgets.QGridLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)

        # Config file
        config_label = QtWidgets.QLabel('Archivo configuración:', self)
        config_btn = QtWidgets.QPushButton('Seleccionar config', self)
        config_btn.clicked.connect(self.selectFile)
        self.config_path = QtWidgets.QLineEdit(self)
        self.config_path.setReadOnly(True)

        # Test folder
        ubicacion_label = QtWidgets.QLabel('Carpeta del ensayo:', self)
        ubicacion_btn = QtWidgets.QPushButton('Abrir ubicación', self)
        ubicacion_btn.clicked.connect(self.selectFolder)
        self.ubicacion_path = QtWidgets.QLineEdit(self)
        self.ubicacion_path.setReadOnly(True)

        # Test name
        texto_label = QtWidgets.QLabel('Nombre del ensayo:', self)
        self.texto_input = QtWidgets.QLineEdit(self)
        aplicar_btn = QtWidgets.QPushButton('Aplicar', self)
        aplicar_btn.clicked.connect(self.applyText)

        vbox_layout.addWidget(config_label, 0, 0)
        vbox_layout.addWidget(self.config_path, 0, 1)
        vbox_layout.addWidget(config_btn, 0, 2)
        vbox_layout.addWidget(ubicacion_label, 1, 0)
        vbox_layout.addWidget(self.ubicacion_path, 1, 1)
        vbox_layout.addWidget(ubicacion_btn, 1, 2)
        vbox_layout.addWidget(texto_label, 2, 0)
        vbox_layout.addWidget(self.texto_input, 2, 1)
        vbox_layout.addWidget(aplicar_btn, 2, 2)
        self.hbox_top.addLayout(vbox_layout)

    def updatePaths(self):
        self.config_path.setText(self.inputReader.config_path)
        self.ubicacion_path.setText(self.inputReader.test_folder)
        self.texto_input.setText(self.inputReader.test_name)

    def selectFile(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, 'Seleccionar archivo', '', 'Archivo yaml (*.yaml)', options=options)
        if file_name:
            self.config_path.setText(file_name)
            # TODO change and load config params

    def selectFolder(self):
        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Seleccionar carpeta', options=options)
        if folder_path:
            self.inputReader.configEdit(
                'test_options.folder', folder_path)
            self.inputReader.loadFiles()
            self.updatePaths()
            self.log_handler.logger.info(
                "Changed folder path to: " + str(folder_path))

    def applyText(self):
        name = self.texto_input.text().strip()
        if not name:
            name = "Ensayo de pruebas"
        self.inputReader.configEdit(
            'test_options.name', name)
        self.inputReader.loadFiles()
        self.updatePaths()
        self.log_handler.logger.info("Changed test name to: " + str(name))

    # MID LAYOUT METHODS
    def loadPanelLayout(self):
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)
        title = QtWidgets.QLabel("Panel")
        title.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)

        self.calibrate_sensors_btn = QtWidgets.QPushButton(
            'Calibrar células', self)
        self.calibrate_sensors_btn.setEnabled(False)
        self.calibrate_sensors_btn.clicked.connect(self.openCalibrationMenu)
        self.start_btn = QtWidgets.QPushButton('Iniciar lectura', self)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.startTest)
        self.vbox_test_check = QtWidgets.QVBoxLayout()
        self.stop_btn = QtWidgets.QPushButton('Finalizar y guardar', self)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stopTest)
        cerrar_btn = QtWidgets.QPushButton('Cerrar programa', self)
        cerrar_btn.clicked.connect(self.close)

        vbox_layout.addWidget(title)
        vbox_layout.addWidget(self.calibrate_sensors_btn)
        vbox_layout.addWidget(self.start_btn)
        vbox_layout.addLayout(self.vbox_test_check)
        vbox_layout.addWidget(self.stop_btn)
        vbox_layout.addWidget(cerrar_btn)
        self.hbox_mid.addLayout(vbox_layout)

    def loadSensorLayout(self):
        vbox_layout = QtWidgets.QVBoxLayout()
        vbox_layout.setAlignment(QtCore.Qt.AlignTop)

        # First layout with title and sensor update button
        hbox_title_layout = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Información sensores")
        title.setFont(QtGui.QFont("Arial", 14, QtGui.QFont.Bold))
        title.setAlignment(QtCore.Qt.AlignCenter)

        update_sensors_btn = QtWidgets.QPushButton(
            'Conectar sensores', self)
        update_sensors_btn.setMaximumWidth(200)
        update_sensors_btn.clicked.connect(self.updateSensors)

        hbox_title_layout.addWidget(update_sensors_btn)
        hbox_title_layout.addWidget(title)

        # Sensor grid
        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)
        grid_layout.setAlignment(QtCore.Qt.AlignTop)

        vbox_p1 = QtWidgets.QVBoxLayout()
        vbox_p1.addWidget(QtWidgets.QLabel("Plataforma 1"))
        vbox_p2 = QtWidgets.QVBoxLayout()
        vbox_p2.addWidget(QtWidgets.QLabel("Plataforma 2"))
        vbox_p3 = QtWidgets.QVBoxLayout()
        vbox_p3.addWidget(QtWidgets.QLabel("Sensores externos"))
        grid_layout.addLayout(vbox_p1, 0, 0)
        grid_layout.addLayout(vbox_p2, 0, 1)
        grid_layout.addLayout(vbox_p3, 0, 2)

        # Sensor information
        vbox_p1.addLayout(self.loadSensorGridLayout(
            self.inputReader.getPlatform1SensorStatus(), self.handlePlatform1SensorCheckbox))
        vbox_p2.addLayout(self.loadSensorGridLayout(
            self.inputReader.getPlatform2SensorStatus(), self.handlePlatform2SensorCheckbox))
        vbox_p3.addLayout(self.loadSensorGridLayout(
            self.inputReader.getEncoderSensorsStatus(), self.handleEncoderCheckbox))
        vbox_p3.addLayout(self.loadSensorGridLayout(
            self.inputReader.getIMUSensorStatus(), self.handleIMUCheckbox))

        vbox_layout.addLayout(hbox_title_layout)
        vbox_layout.addLayout(grid_layout)
        self.hbox_mid.addLayout(vbox_layout)

    def updateSensors(self):
        # Connect sensors
        self.inputReader.connectSensors()
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

    def loadSensorGridLayout(self, status_list, checkbox_handler):
        loadcell_layout = QtWidgets.QGridLayout()
        loadcell_layout.setColumnStretch(0, 0)
        loadcell_layout.setColumnStretch(1, 0)
        loadcell_layout.setColumnStretch(2, 1)
        loadcell_layout.setColumnMinimumWidth(0, 25)
        loadcell_layout.setColumnMinimumWidth(1, 20)
        loadcell_layout.setHorizontalSpacing(5)
        loadcell_layout.setVerticalSpacing(5)
        loadcell_layout.setAlignment(QtCore.Qt.AlignLeft)
        # TODO avoid accessing specific keys here
        for i, sensor in enumerate(status_list):
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(sensor['read_data'])
            checkbox.setObjectName(sensor['id'])
            checkbox.stateChanged.connect(checkbox_handler)
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

    # TODO avoid accessing specific config keys here!!
    def handlePlatform1SensorCheckbox(self, state):
        sender = self.sender()
        self.inputReader.configEdit(
            'p1_phidget_loadcell_list.' + sender.objectName() + '.read_data', state == 2)

    def handlePlatform2SensorCheckbox(self, state):
        sender = self.sender()
        self.inputReader.configEdit(
            'p2_phidget_loadcell_list.' + sender.objectName() + '.read_data', state == 2)

    def handleEncoderCheckbox(self, state):
        sender = self.sender()
        self.inputReader.configEdit(
            'phidget_encoder_list.' + sender.objectName() + '.read_data', state == 2)

    def handleIMUCheckbox(self, state):
        sender = self.sender()
        self.inputReader.configEdit(
            'taobotics_imu_list.' + sender.objectName() + '.read_data', state == 2)

    def updateTestChecks(self):
        test_status_text = [
            ('Config cargada', '(!!) Pendiente cargar config'),
            ('Ubicación seleccionada', '(!!) Selecciona ubicación para el ensayo'),
            ('Nombre del ensayo definido', '(!!) Asigna un nombre de ensayo'),
            ('Conexión establecida', '(!!) Conecta al menos un sensor')]
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
        self.stop_btn.setEnabled(True)
        self.timer.start(10)  # ms

    def stopTest(self):
        self.stop_btn.setEnabled(False)
        self.timer.stop()
        self.inputReader.readerStop()
        self.start_btn.setEnabled(True)
        self.calibrate_sensors_btn.setEnabled(True)

    def openCalibrationMenu(self):
        self.interface.hide()
        self.calibrationmenu = MainCalibrationMenu(self, self.inputReader)
        self.interface_box.addWidget(self.calibrationmenu)
        self.calibrationmenu.show()

    # TODO BOTTOM LAYOUT METHODS
    # def generateExamplePlots(self):
    #     vbox_plot1 = QVBoxLayout()
    #     vbox_plot2 = QVBoxLayout()
    #     vbox_plot3 = QVBoxLayout()

    #     # Plot titles
    #     title_plot1 = QLabel("Plot 1")
    #     title_plot1.setFont(QFont("Arial", 14, QFont.Bold))
    #     title_plot1.setAlignment(Qt.AlignCenter)
    #     title_plot2 = QLabel("Plot 2")
    #     title_plot2.setFont(QFont("Arial", 14, QFont.Bold))
    #     title_plot2.setAlignment(Qt.AlignCenter)
    #     title_plot3 = QLabel("Plot 3")
    #     title_plot3.setFont(QFont("Arial", 14, QFont.Bold))
    #     title_plot3.setAlignment(Qt.AlignCenter)

    #     # Example plots
    #     # y = np.random.normal(loc=0.5, scale=0.4, size=1000)
    #     # y = y[(y > -0.3) & (y < 0.3)]
    #     # y.sort()
    #     y = np.linspace(0, 0, 100)
    #     x = np.arange(len(y))
    #     fig1, ax1 = plt.subplots()
    #     canvas1 = FigureCanvas(fig1)
    #     toolbar1 = NavigationToolbar(canvas1, self)
    #     ax1.plot(x,y)
    #     ax1.grid(True)

    #     fig2, ax2 = plt.subplots()
    #     canvas2 = FigureCanvas(fig2)
    #     toolbar2 = NavigationToolbar(canvas2, self)
    #     ax2.plot(x,y)
    #     ax2.grid(True)

    #     fig3, ax3 = plt.subplots()
    #     canvas3 = FigureCanvas(fig3)
    #     toolbar3 = NavigationToolbar(canvas3, self)
    #     ax3.plot(x,y)
    #     ax3.grid(True)

    #     # Layouts
    #     vbox_plot1.addWidget(title_plot1)
    #     vbox_plot1.addWidget(toolbar1)
    #     vbox_plot1.addWidget(canvas1)
    #     vbox_plot2.addWidget(title_plot2)
    #     vbox_plot2.addWidget(toolbar2)
    #     vbox_plot2.addWidget(canvas2)
    #     vbox_plot3.addWidget(title_plot3)
    #     vbox_plot3.addWidget(toolbar3)
    #     vbox_plot3.addWidget(canvas3)

    #     self.hbox_bottom.addLayout(vbox_plot1)
    #     self.hbox_bottom.addLayout(vbox_plot2)
    #     self.hbox_bottom.addLayout(vbox_plot3)
