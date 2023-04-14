# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 13/04/2023
"""

import os
# import numpy as np
# import matplotlib.pyplot as plt

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QGridLayout, QFileDialog, QLineEdit, QCheckBox, QDesktopWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QIcon, QFont
from PyQt5.QtCore import Qt
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from src.inputReader import InputReader
from src.utils import LogHandler


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.log_handler = LogHandler(str(__class__.__name__))

    def initUI(self):
        self.setWindowTitle('Programa de lecturas')
        self.setWindowIcon(QIcon('logo.ico'))
        screen_resolution = QDesktopWidget().screenGeometry()
        width, height = screen_resolution.width(), screen_resolution.height()
        self.setGeometry(width//4, height//4, width//2, height//2)

        # Main GUI layouts
        hbox_main = QVBoxLayout()
        self.hbox_top = QHBoxLayout()
        self.hbox_mid = QHBoxLayout()
        self.hbox_bottom = QHBoxLayout()

        # Inner layouts
        vbox_logo = QVBoxLayout()
        vbox_files = QVBoxLayout()
        vbox_panel = QVBoxLayout()
        vbox_sensors = QVBoxLayout()

        # Spacers
        spacer_20 = QSpacerItem(
            20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum)

        # Inner layouts adjustments
        self.hbox_top.setAlignment(Qt.AlignTop)
        self.hbox_mid.setAlignment(Qt.AlignTop)
        self.hbox_bottom.setAlignment(Qt.AlignBottom)

        # Build
        hbox_main.setAlignment(Qt.AlignTop)
        hbox_main.addLayout(self.hbox_top)
        hbox_main.addItem(spacer_20)
        hbox_main.addLayout(self.hbox_mid)
        hbox_main.addItem(spacer_20)
        hbox_main.addLayout(self.hbox_bottom)
        self.setLayout(hbox_main)

        # Load reader software and layouts
        self.inputReader = InputReader()

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
        vbox_layout = QVBoxLayout()
        vbox_layout.setAlignment(Qt.AlignTop)

        image = QLabel(self)
        pixmap = QPixmap('logo.ico')
        image.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio))
        image.setAlignment(Qt.AlignCenter)
        label = QLabel('Plataforma fuerza', self)
        label.setFont(QFont("Arial", 12, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)

        vbox_layout.addWidget(image)
        vbox_layout.addWidget(label)
        self.hbox_top.addLayout(vbox_layout)

    def loadFilesLayout(self):
        vbox_layout = QGridLayout()
        vbox_layout.setAlignment(Qt.AlignTop)

        # Config file
        config_label = QLabel('Archivo configuración:', self)
        config_btn = QPushButton('Seleccionar config', self)
        config_btn.clicked.connect(self.select_file)
        self.config_path = QLineEdit(self)
        self.config_path.setReadOnly(True)

        # Test folder
        ubicacion_label = QLabel('Carpeta del ensayo:', self)
        ubicacion_btn = QPushButton('Abrir ubicación', self)
        ubicacion_btn.clicked.connect(self.select_folder)
        self.ubicacion_path = QLineEdit(self)
        self.ubicacion_path.setReadOnly(True)

        # Test name
        texto_label = QLabel('Nombre del ensayo:', self)
        self.texto_input = QLineEdit(self)
        aplicar_btn = QPushButton('Aplicar', self)
        aplicar_btn.clicked.connect(self.apply_text)

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

    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name, _ = QFileDialog.getOpenFileName(
            self, 'Seleccionar archivo', '', 'Archivo yaml (*.yaml)', options=options)
        if file_name:
            self.config_path.setText(file_name)

    def select_folder(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        folder_name = QFileDialog.getExistingDirectory(
            self, 'Seleccionar carpeta', options=options)
        if folder_name:
            self.ubicacion_path.setText(folder_name)

    def apply_text(self):
        pass

    # MID LAYOUT METHODS
    def loadPanelLayout(self):
        vbox_layout = QVBoxLayout()
        vbox_layout.setAlignment(Qt.AlignTop)
        title = QLabel("Panel")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        calibrate_sensors_btn = QPushButton('Calibrar células', self)
        calibrate_sensors_btn.setEnabled(False)
        self.start_btn = QPushButton('Iniciar lectura', self)
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.startTest)
        self.vbox_test_check = QVBoxLayout()
        self.stop_btn = QPushButton('Finalizar y guardar', self)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stopTest)
        cerrar_btn = QPushButton('Cerrar programa', self)
        cerrar_btn.clicked.connect(self.close)

        vbox_layout.addWidget(title)
        vbox_layout.addWidget(calibrate_sensors_btn)
        vbox_layout.addWidget(self.start_btn)
        vbox_layout.addLayout(self.vbox_test_check)
        vbox_layout.addWidget(self.stop_btn)
        vbox_layout.addWidget(cerrar_btn)
        self.hbox_mid.addLayout(vbox_layout)

    def loadSensorLayout(self):
        vbox_layout = QVBoxLayout()
        vbox_layout.setAlignment(Qt.AlignTop)

        # First layout with title and sensor update button
        hbox_title_layout = QHBoxLayout()
        title = QLabel("Información sensores")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)

        update_sensors_btn = QPushButton(
            'Conectar sensores seleccionados', self)
        update_sensors_btn.setMaximumWidth(200)
        update_sensors_btn.clicked.connect(self.updateSensors)

        hbox_title_layout.addWidget(update_sensors_btn)
        hbox_title_layout.addWidget(title)

        # Sensor grid
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 1)
        grid_layout.setColumnStretch(2, 1)
        grid_layout.setAlignment(Qt.AlignTop)

        vbox_p1 = QVBoxLayout()
        vbox_p1.addWidget(QLabel("Plataforma 1"))
        vbox_p2 = QVBoxLayout()
        vbox_p2.addWidget(QLabel("Plataforma 2"))
        vbox_p3 = QVBoxLayout()
        vbox_p3.addWidget(QLabel("Otros sensores"))
        grid_layout.addLayout(vbox_p1, 0, 0)
        grid_layout.addLayout(vbox_p2, 0, 1)
        grid_layout.addLayout(vbox_p3, 0, 2)

        # Sensor information
        vbox_p1.addLayout(self.loadPlatformLoadCellsLayout(1))
        # TODO vbox_p2.addLayout(self.loadPlatformLoadCellsLayout(2))

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
                        elif element.layout() is not None and isinstance(element, QGridLayout):
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

    def loadPlatformLoadCellsLayout(self, platformNumber):
        loadcell_layout = QGridLayout()
        loadcell_layout.setColumnStretch(0, 0)
        loadcell_layout.setColumnStretch(1, 0)
        loadcell_layout.setColumnStretch(2, 1)
        loadcell_layout.setColumnMinimumWidth(0, 25)
        loadcell_layout.setColumnMinimumWidth(1, 20)
        loadcell_layout.setHorizontalSpacing(5)
        loadcell_layout.setVerticalSpacing(5)
        loadcell_layout.setAlignment(Qt.AlignLeft)
        for i, sensor in enumerate(self.inputReader.getSensorStatus()):
            checkbox = QCheckBox()
            checkbox.setChecked(sensor['read_data'])
            checkbox.setObjectName(sensor['id'])
            checkbox.stateChanged.connect(self.handleSensorCheckbox)
            loadcell_layout.addWidget(checkbox, i, 0)

            label = QLabel()
            label.setStyleSheet('background-color: grey')
            if sensor['status'] == 'Disconnected':
                label.setStyleSheet('background-color: red')
            elif sensor['status'] == 'Active':
                label.setStyleSheet('background-color: green')
            loadcell_layout.addWidget(label, i, 1)

            label = QLabel(sensor['name'])
            loadcell_layout.addWidget(label, i, 2)
        return loadcell_layout

    def handleSensorCheckbox(self, state):
        sender = self.sender()
        self.inputReader.configEdit(
            'load_cell_list.' + sender.objectName() + '.read_data', state == 2)

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
            label = QLabel(output)
            label.setMinimumSize(20, 20)
            label.setStyleSheet("color: green;")
            if not ok:
                label.setStyleSheet("color: red;")
                test_available = False
            self.vbox_test_check.addWidget(label)

        self.start_btn.setEnabled(test_available)

    def startTest(self):
        self.start_btn.setEnabled(False)
        self.inputReader.readerStart()
        self.stop_btn.setEnabled(True)

    def stopTest(self):
        self.stop_btn.setEnabled(False)
        self.inputReader.readerStop()
        self.start_btn.setEnabled(True)
    
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
    #     fig1, ax1 = plt.subplots()
    #     canvas1 = FigureCanvas(fig1)
    #     toolbar1 = NavigationToolbar(canvas1, self)
    #     ax1.plot(np.linspace(0, 10, 100), np.sin(np.linspace(0, 10, 100)))

    #     fig2, ax2 = plt.subplots()
    #     canvas2 = FigureCanvas(fig2)
    #     toolbar2 = NavigationToolbar(canvas2, self)
    #     ax2.plot(np.linspace(0, 10, 100), np.cos(np.linspace(0, 10, 100)))

    #     fig3, ax3 = plt.subplots()
    #     canvas3 = FigureCanvas(fig3)
    #     toolbar3 = NavigationToolbar(canvas3, self)
    #     ax3.plot(np.linspace(0, 10, 100), np.tan(np.linspace(0, 10, 100)))

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
