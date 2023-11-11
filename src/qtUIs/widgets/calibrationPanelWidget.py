# -*- coding: utf-8 -*-

from PySide6 import QtWidgets, QtGui, QtCore
from src.enums.qssLabels import QssLabels
from src.managers.calibrationManager import CalibrationManager
from src.qtUIs.widgets.matplotlibWidgets import PlotRegressionWidget


class CalibrationPanelWidget(QtWidgets.QWidget):
    def __init__(self, calib_mngr: CalibrationManager):
        super(CalibrationPanelWidget, self).__init__()
        self.calib_mngr = calib_mngr

        self.recording_timer = QtCore.QTimer(self)
        self.recording_timer.timeout.connect(self.calib_mngr.registerValue)

        self.setLayout(self.loadLayout())

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

    # UI section loaders

    def loadLayout(self) -> QtWidgets.QVBoxLayout:
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        # Sensor info and main buttons
        hbox_info_layout = QtWidgets.QHBoxLayout()

        group_box_sensor_info = QtWidgets.QGroupBox("Sensor information")
        self.vbox_sensor_info_layout = QtWidgets.QVBoxLayout()
        self.vbox_sensor_info_layout.setAlignment(QtCore.Qt.AlignTop)
        group_box_sensor_info.setLayout(self.vbox_sensor_info_layout)
        self.sensor_info_label = self.createLabelBox(
            "Select an available sensor", QssLabels.STATUS_LABEL_WARN
        )
        self.vbox_sensor_info_layout.addWidget(self.sensor_info_label)

        group_box_general_buttons = QtWidgets.QGroupBox("Manage results")
        self.grid_buttons_layout = QtWidgets.QGridLayout()
        group_box_general_buttons.setLayout(self.grid_buttons_layout)
        self.save_button = self.createQPushButton(
            "Save results", QssLabels.CONTROL_PANEL_BTN, enabled=False
        )
        self.clear_button = self.createQPushButton(
            "Clear calibration test",
            QssLabels.CRITICAL_CONTROL_PANEL_BTN,
            enabled=False,
        )
        self.grid_buttons_layout.addWidget(self.save_button, 0, 0)
        self.grid_buttons_layout.addWidget(self.clear_button, 0, 1)

        hbox_info_layout.addWidget(group_box_sensor_info)
        hbox_info_layout.addWidget(group_box_general_buttons)

        # Calibration info
        group_box_calibration = QtWidgets.QGroupBox("Measurements for calibration")
        vbox_calibration_layout = QtWidgets.QVBoxLayout()
        vbox_calibration_layout.setAlignment(QtCore.Qt.AlignTop)
        group_box_calibration.setLayout(vbox_calibration_layout)

        # - Measurements TableWidget
        self.measurements_widget = QtWidgets.QTableWidget(0, 4)
        self.measurements_widget.setHorizontalHeaderLabels(
            ["Test value", "Sensor mean", "Sensor STD", "Num. of measurements"]
        )
        self.measurements_widget.verticalHeader().setVisible(False)
        self.measurements_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        # - Measure control buttons
        grid_measure_btns_layout = QtWidgets.QGridLayout()
        self.auto_measure_button = self.createQPushButton(
            "Measure with sensor", enabled=False, connect_fn=self.recordDataWithSensor
        )
        self.manual_measure_button = self.createQPushButton(
            "Measure with value", enabled=False, connect_fn=self.recordData
        )
        self.test_value_input = QtWidgets.QLineEdit()
        self.test_value_input.setPlaceholderText(
            "Enter calibration value: (example) 14.67"
        )
        self.remove_row_button = self.createQPushButton(
            "Remove selected row",
            QssLabels.CRITICAL_BTN,
            enabled=False,
            connect_fn=self.removeRow,
        )
        self.test_value_input.setDisabled(True)
        self.test_value_input.textChanged.connect(self.onTextChanged)
        grid_measure_btns_layout.addWidget(self.auto_measure_button, 0, 0)
        grid_measure_btns_layout.addWidget(self.manual_measure_button, 0, 1)
        grid_measure_btns_layout.addWidget(self.test_value_input, 0, 2)
        grid_measure_btns_layout.addWidget(self.remove_row_button, 0, 3)

        # -  Results TableWidget
        self.calib_results_widget = QtWidgets.QTableWidget(3, 1)
        self.calib_results_widget.setVerticalHeaderLabels(
            ["Slope (m)", "Intercept (b)", "Score (r2)"]
        )
        self.calib_results_widget.horizontalHeader().setVisible(False)
        self.calib_results_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.calib_results_widget.setMaximumHeight(
            self.calib_results_widget.verticalHeader().length() + 6
        )
        self.scope_result_label = QtWidgets.QLabel("0")
        self.intercept_result_label = QtWidgets.QLabel("0")
        self.score_result_label = QtWidgets.QLabel("0")
        self.calib_results_widget.setCellWidget(0, 0, self.scope_result_label)
        self.calib_results_widget.setCellWidget(1, 0, self.intercept_result_label)
        self.calib_results_widget.setCellWidget(2, 0, self.score_result_label)

        # - PlotWidget to plot measurements
        self.plot_widget = PlotRegressionWidget()

        self.generate_results_button = self.createQPushButton(
            "Make linear regression",
            enabled=False,
            connect_fn=self.generateResults,
        )

        # - Build calibration layout
        vbox_calibration_layout.addWidget(self.measurements_widget)
        vbox_calibration_layout.addLayout(grid_measure_btns_layout)
        vbox_calibration_layout.addWidget(self.plot_widget)
        vbox_calibration_layout.addWidget(self.generate_results_button)
        vbox_calibration_layout.addWidget(self.calib_results_widget)

        # Build main layout
        main_layout.addLayout(hbox_info_layout)
        main_layout.addItem(QtWidgets.QSpacerItem(10, 10))
        main_layout.addWidget(group_box_calibration)
        main_layout.addItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
        )

        return main_layout

    # UI buttons click connectors

    @QtCore.Slot()
    def onTextChanged(self):
        try:
            float(self.test_value_input.text())
            self.manual_measure_button.setEnabled(True)
        except ValueError:
            self.manual_measure_button.setEnabled(False)

    @QtCore.Slot()
    def recordData(self):
        test_value = float(self.test_value_input.text())
        self.enableButtons(False)
        self.calib_mngr.startRecording()
        self.recording_timer.start(self.calib_mngr.getCalibTestInterval())
        QtCore.QTimer.singleShot(
            self.calib_mngr.getCalibDuration(), self.recording_timer.stop
        )
        while self.recording_timer.isActive():
            QtCore.QCoreApplication.processEvents()
        self.calib_mngr.stopRecording()
        values = self.calib_mngr.getValues(test_value)
        self.addMeasurementRow(values[0], values[1], values[2], values[3])
        sensor_values, test_values = self.calib_mngr.getValuesArrays()
        self.plot_widget.updateScatter(sensor_values, test_values)
        self.enableButtons(True)

    @QtCore.Slot()
    def recordDataWithSensor(self):
        pass

    @QtCore.Slot()
    def removeRow(self):
        self.enableButtons(False)
        selected_row = self.measurements_widget.currentRow()
        if selected_row >= 0:
            self.measurements_widget.removeRow(selected_row)
            self.calib_mngr.removeValueSet(selected_row)
        sensor_values, test_values = self.calib_mngr.getValuesArrays()
        self.plot_widget.updateScatter(sensor_values, test_values)
        self.enableButtons(True)

    @QtCore.Slot()
    def generateResults(self):
        results = self.calib_mngr.getRegressionResults()
        self.updateResultsTable(results[0], results[1], results[2])
        sensor_values, calib_values = self.calib_mngr.getRegressionArrays()
        self.plot_widget.updateRegression(sensor_values, calib_values)

    @QtCore.Slot()
    def saveResults(self):
        pass

    @QtCore.Slot()
    def clearValues(self):
        pass

    # Widget functions

    def selectPlatformSensor(self, index, platform):
        sensor_info = ["Name error", "Properties error"]
        if platform == 1:
            sensor_info = self.calib_mngr.calibrateP1Sensor(index)
        if platform == 2:
            sensor_info = self.calib_mngr.calibrateP2Sensor(index)
        if sensor_info[0] == "Name error":
            print("Could not load desired sensor!")
            return
        self.updateSensorInformation(sensor_info[0], sensor_info[1])
        self.enableButtons(True)

    def updateSensorInformation(self, name: str, properties: str):
        self.sensor_info_label.setParent(None)
        self.sensor_info_label = self.createLabelBox(
            f"Name: {name}\nProperties: {properties}", QssLabels.STATUS_LABEL_INFO
        )
        self.vbox_sensor_info_layout.addWidget(self.sensor_info_label)

    def enableButtons(self, enable: bool = False):
        if not enable:
            self.save_button.setEnabled(enable)
            self.auto_measure_button.setEnabled(enable)
            self.remove_row_button.setEnabled(enable)
            self.generate_results_button.setEnabled(enable)
        if self.calib_mngr.refSensorConnected():
            self.auto_measure_button.setEnabled(enable)
        if self.measurements_widget.rowCount() > 0:
            self.remove_row_button.setEnabled(enable)
        if self.measurements_widget.rowCount() > 1:
            self.generate_results_button.setEnabled(enable)
        self.test_value_input.setEnabled(enable)
        self.manual_measure_button.setEnabled(enable)
        self.clear_button.setEnabled(enable)

    def addMeasurementRow(
        self,
        test_value: float,
        sensor_mean: float,
        sensor_std: float,
        measurements: int,
    ):
        row_position = self.measurements_widget.rowCount()
        self.measurements_widget.insertRow(row_position)
        self.measurements_widget.setItem(
            row_position, 0, QtWidgets.QTableWidgetItem("{:.6e}".format(test_value))
        )
        self.measurements_widget.setItem(
            row_position, 1, QtWidgets.QTableWidgetItem("{:.6e}".format(sensor_mean))
        )
        self.measurements_widget.setItem(
            row_position, 2, QtWidgets.QTableWidgetItem("{:.6e}".format(sensor_std))
        )
        self.measurements_widget.setItem(
            row_position, 3, QtWidgets.QTableWidgetItem(str(measurements))
        )

    def updateResultsTable(self, scope: float, intercept: float, score: float):
        self.scope_result_label.setText("{:.6e}".format(scope))
        self.intercept_result_label.setText("{:.6e}".format(intercept))
        self.score_result_label.setText("{:.4f}".format(score))
