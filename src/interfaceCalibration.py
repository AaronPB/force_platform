# -*- coding: utf-8 -*-
"""
Author: Aaron Poyatos
Date: 15/05/2023
"""

import time

from PyQt5 import QtWidgets, QtCore
from src.inputReader import InputReader
from src.utils import LogHandler


class MainCalibrationMenu(QtWidgets.QWidget):
    def __init__(self, parent, inputReader: InputReader):
        super().__init__(parent)
        self.parent = parent
        self.log_handler = LogHandler(str(__class__.__name__))
        self.inputReader = inputReader
        self.calibration_timer = QtCore.QTimer(self)
        self.calibration_timer.timeout.connect(
            self.inputReader.calibrateTestProcess)
        self.initUI()

    def initUI(self):
        self.main_vbox_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_vbox_layout)
        self.grid_layout = QtWidgets.QGridLayout()
        self.main_vbox_layout.addLayout(self.grid_layout)

        # Column labels
        self.grid_layout.addWidget(QtWidgets.QLabel("Plataforma 1"), 0, 0)
        self.grid_layout.addWidget(QtWidgets.QLabel("Plataforma 2"), 0, 1)
        self.grid_layout.addWidget(QtWidgets.QLabel("Otros sensores"), 0, 2)

        # Load sensor grid
        self.loadSensorButtons(
            1, 0, self.inputReader.getPlatform1SensorStatus())
        self.loadSensorButtons(
            1, 1, self.inputReader.getPlatform2SensorStatus())
        offset = self.loadSensorButtons(
            1, 2, self.inputReader.getEncoderSensorsStatus())
        # self.loadSensorButtons(
        #     offset+1, 2, self.inputReader.getIMUSensorStatus())

        # Add close button
        self.close_button = QtWidgets.QPushButton('Cerrar y guardar', self)
        self.close_button.clicked.connect(self.close)
        self.grid_layout.addWidget(self.close_button, 13, 0, 1, 3)

        self.show()

    def loadSensorButtons(self, row_offset: int, column_number: int, sensor_list: list):
        # Sensor list
        for i, sensor in enumerate(sensor_list):
            row = i + row_offset
            sensor_button = QtWidgets.QPushButton(sensor['name'], self)
            sensor_button.clicked.connect(
                lambda state, s=sensor: self.calibrationDialog(s))
            if not sensor['read_data'] or sensor['status'] != 'Active':
                sensor_button.setEnabled(False)
            self.grid_layout.addWidget(sensor_button, row, column_number)
        return row

    def calibrationDialog(self, sensor):
        # Unique sensor input
        calibration_prepared = self.inputReader.prepareSensorCalibration(
            sensor['name'])
        self.log_handler.logger.info(
            'Calibration status: ' + str(calibration_prepared))
        if not calibration_prepared:
            return

        calibration_dialog = QtWidgets.QDialog()
        calibration_dialog.setWindowTitle(
            'Calibración del sensor ' + str(sensor['name']))
        calibration_dialog.resize(800, 400)
        calibration_dialog_layout = QtWidgets.QVBoxLayout(calibration_dialog)
        calibration_dialog_layout.setAlignment(QtCore.Qt.AlignTop)

        # Sensor name
        sensor_name_label = QtWidgets.QLabel(sensor['name'])
        sensor_name_label.setAlignment(QtCore.Qt.AlignHCenter)
        calibration_dialog_layout.addWidget(sensor_name_label)

        # Calibration test values
        self.text_list_widget = QtWidgets.QListWidget(self)
        self.text_values_list = []
        self.text_list_widget.addItem(
            "Value \t\tSensor mean \tSensor STD \t Num. of measurements")
        calibration_dialog_layout.addWidget(
            QtWidgets.QLabel('Mediciones realizadas'))
        calibration_dialog_layout.addWidget(self.text_list_widget)

        # Calibration results
        self.text_calibration_widget = QtWidgets.QListWidget(self)
        self.text_calibration_list = []
        self.text_calibration_widget.addItem("Scope (m):\t\t-")
        self.text_calibration_widget.addItem("Intercept (b):\t-")
        self.text_calibration_widget.addItem("Score (r2):\t\t-")
        calibration_dialog_layout.addWidget(
            QtWidgets.QLabel('Resultados de la regresión lineal'))
        calibration_dialog_layout.addWidget(self.text_calibration_widget)

        # Calibration input value
        self.test_value_input = QtWidgets.QLineEdit()
        self.test_value_input.setPlaceholderText(
            'Introduce el valor de calibración: (ejemplo) 14.67')
        calibration_dialog_layout.addWidget(self.test_value_input)

        # Dialog buttons
        button_box = QtWidgets.QHBoxLayout()
        self.measure_button = QtWidgets.QPushButton('Medir')
        self.measure_button.clicked.connect(self.executeTest)
        self.calibrate_button = QtWidgets.QPushButton('Calibrar')
        self.calibrate_button.clicked.connect(self.calibrationResults)
        self.save_button = QtWidgets.QPushButton('Finalizar')
        self.save_button.clicked.connect(
            lambda: self.toMainMenu(calibration_dialog))
        cancel_button = QtWidgets.QPushButton('Cancelar')
        cancel_button.clicked.connect(calibration_dialog.reject)
        button_box.addWidget(self.measure_button)
        button_box.addWidget(self.calibrate_button)
        button_box.addWidget(self.save_button)
        button_box.addWidget(cancel_button)
        calibration_dialog_layout.addLayout(button_box)

        calibration_dialog.exec_()

    def toMainMenu(self, sensor_dialog):
        # Cerrar el diálogo de calibración y volver al menú principal
        sensor_dialog.accept()

    def executeTest(self):
        # Get input value
        text = self.test_value_input.text()
        value = -1
        try:
            value = float(text)
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 'Error', 'Debe ingresar un número decimal.')
            return

        # Execute calibration test
        self.inputReader.calibrationNewTest(value)
        self.measure_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)
        self.calibration_timer.start(10)
        QtCore.QTimer.singleShot(2000, self.calibration_timer.stop)

        while self.calibration_timer.isActive():
            QtCore.QCoreApplication.processEvents()

        self.measure_button.setEnabled(True)
        self.calibrate_button.setEnabled(True)

        mean, std, measurements = self.inputReader.getCalibrateTestResults()

        if not mean:
            return

        # Update text list widget
        test_results = str(value) + "\t\t" + str(mean) + \
            "\t" + str(std) + "\t" + str(measurements)
        self.text_list_widget.addItem(test_results)
        self.test_value_input.clear()
        if (self.text_list_widget.count() > 3):
            # TODO enable calibrate results button
            pass
        # self.test_value_input.setPlaceholderText(
        #     'Introduce el valor de calibración: (ejemplo) 14.67')

    def calibrationResults(self):
        # Get results
        slope, intercept, score = self.inputReader.getCalibrateRegressionResults()

        # Update calibration list widget
        self.text_calibration_widget.clear()
        self.text_calibration_widget.addItem("Scope (m):\t\t" + str(slope))
        self.text_calibration_widget.addItem(
            "Intercept (b):\t" + str(intercept))
        self.text_calibration_widget.addItem("Score (r2):\t\t" + str(score))

    def close(self):
        self.parent.interface.show()
        self.hide()
