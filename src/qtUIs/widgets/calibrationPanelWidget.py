# -*- coding: utf-8 -*-

from PySide6 import QtWidgets, QtCore, QtGui
from src.enums.qssLabels import QssLabels
from src.managers.sensorManager import SensorManager
from src.managers.calibrationManager import SensorCalibrationManager
from src.qtUIs.widgets import customQtLoaders as customQT
from src.qtUIs.widgets.matplotlibWidgets import PlotRegressionWidget


class SensorCalibrationPanelWidget(QtWidgets.QWidget):
    def __init__(
        self,
        sensor_manager: SensorManager,
        sensor_calibration_manager: SensorCalibrationManager,
        sensor_name: str,
        sensor_properties: str,
    ):
        super(SensorCalibrationPanelWidget, self).__init__()
        self.sensor_mngr = sensor_manager
        self.calib_mngr = sensor_calibration_manager
        self.recording_timer = QtCore.QTimer(self)
        self.recording_timer.timeout.connect(self.calib_mngr.registerValue)

        self.sensor_name = sensor_name
        self.sensor_properties = sensor_properties

        self.setLayout(self.loadLayout())

        self.enableButtons(True)

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
        sensor_info_label = customQT.createLabelBox(
            f"Name: {self.sensor_name}\nProperties: {self.sensor_properties}",
            QssLabels.STATUS_LABEL_INFO,
        )
        self.vbox_sensor_info_layout.addWidget(sensor_info_label)

        group_box_general_buttons = QtWidgets.QGroupBox("Manage results")
        self.grid_buttons_layout = QtWidgets.QGridLayout()
        group_box_general_buttons.setLayout(self.grid_buttons_layout)
        self.save_button = customQT.createQPushButton(
            "Save results",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=False,
            connect_fn=self.saveResults,
        )
        self.clear_button = customQT.createQPushButton(
            "Clear calibration test",
            QssLabels.CRITICAL_CONTROL_PANEL_BTN,
            enabled=False,
            connect_fn=self.clearValues,
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
        self.auto_measure_button = customQT.createQPushButton(
            "Measure with sensor", enabled=False, connect_fn=self.recordDataWithSensor
        )
        self.manual_measure_button = customQT.createQPushButton(
            "Measure with value", enabled=False, connect_fn=self.recordData
        )
        self.test_value_input = QtWidgets.QLineEdit()
        self.test_value_input.setPlaceholderText("Enter calibration value: (ex) 14.67")
        self.remove_row_button = customQT.createQPushButton(
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

        self.generate_results_button = customQT.createQPushButton(
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
        self.calib_mngr.startMeasurement(ref_value=test_value)
        self.recording_timer.start(self.calib_mngr.getRecordInterval())
        QtCore.QTimer.singleShot(
            self.calib_mngr.getRecordDuration(), self.recording_timer.stop
        )
        while self.recording_timer.isActive():
            QtCore.QCoreApplication.processEvents()
        self.calib_mngr.stopMeasurement()
        values = self.calib_mngr.getLastValues()
        self.addMeasurementRow(values[0], values[1], values[2], values[3])
        sensor_values, test_values = self.calib_mngr.getValuesArrays()
        self.plot_widget.updateScatter(sensor_values, test_values)
        self.enableButtons(True)

    @QtCore.Slot()
    def recordDataWithSensor(self):
        self.enableButtons(False)
        self.calib_mngr.startMeasurement(use_ref_sensor=True)
        self.recording_timer.start(self.calib_mngr.getRecordInterval())
        QtCore.QTimer.singleShot(
            self.calib_mngr.getRecordDuration(), self.recording_timer.stop
        )
        while self.recording_timer.isActive():
            QtCore.QCoreApplication.processEvents()
        self.calib_mngr.stopMeasurement()
        values = self.calib_mngr.getLastValues()
        self.addMeasurementRow(values[0], values[1], values[2], values[3])
        sensor_values, test_values = self.calib_mngr.getValuesArrays()
        self.plot_widget.updateScatter(sensor_values, test_values)
        self.enableButtons(True)

    @QtCore.Slot()
    def removeRow(self):
        self.enableButtons(False)
        selected_row = self.measurements_widget.currentRow()
        if selected_row >= 0:
            self.measurements_widget.removeRow(selected_row)
            self.calib_mngr.removeMeasurement(selected_row)
        sensor_values, test_values = self.calib_mngr.getValuesArrays()
        self.plot_widget.updateScatter(sensor_values, test_values)
        self.enableButtons(True)

    @QtCore.Slot()
    def generateResults(self):
        results = self.calib_mngr.getResults()
        self.updateResultsTable(results[0], results[1], results[2])
        sensor_values, calib_values = self.calib_mngr.getRegressionArrays()
        self.plot_widget.updateRegression(sensor_values, calib_values)
        self.save_button.setEnabled(True)

    @QtCore.Slot()
    def saveResults(self):
        self.calib_mngr.saveResults(self.sensor_mngr)
        self.save_button.setEnabled(False)

    @QtCore.Slot()
    def clearValues(self):
        self.enableButtons(False)
        self.clearCalibrationTest()
        self.enableButtons(True)

    # Widget functions

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

    def clearCalibrationTest(self):
        self.test_value_input.clear()
        self.measurements_widget.clearContents()
        self.measurements_widget.setRowCount(0)
        self.plot_widget.clear()
        self.updateResultsTable(0, 0, 0)
        self.calib_mngr.clearValues()


class PlatformCalibrationPanelWidget(QtWidgets.QWidget):
    def __init__(
        self,
        sensor_manager: SensorManager,
        # platform_calibration_manager: SensorCalibrationManager,
        platform_name: str,
    ):
        super(PlatformCalibrationPanelWidget, self).__init__()
        self.sensor_mngr = sensor_manager
        # self.calib_mngr = platform_calibration_manager
        # self.recording_timer = QtCore.QTimer(self)
        # self.recording_timer.timeout.connect(self.calib_mngr.registerValue)

        self.platform_name = platform_name

        self.setLayout(self.loadLayout())

        # self.enableButtons(True)

    # UI section loaders

    def loadLayout(self) -> QtWidgets.QVBoxLayout:
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        # Sensor info and main buttons
        hbox_info_layout = QtWidgets.QHBoxLayout()

        group_box_sensor_info = QtWidgets.QGroupBox("Platform information")
        self.vbox_sensor_info_layout = QtWidgets.QVBoxLayout()
        self.vbox_sensor_info_layout.setAlignment(QtCore.Qt.AlignTop)
        group_box_sensor_info.setLayout(self.vbox_sensor_info_layout)
        sensor_info_label = customQT.createLabelBox(
            f"Name: {self.platform_name}",
            QssLabels.STATUS_LABEL_INFO,
        )
        self.vbox_sensor_info_layout.addWidget(sensor_info_label)

        group_box_general_buttons = QtWidgets.QGroupBox("Manage results")
        self.grid_buttons_layout = QtWidgets.QGridLayout()
        group_box_general_buttons.setLayout(self.grid_buttons_layout)
        self.save_button = customQT.createQPushButton(
            "Save results",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=False,
            # connect_fn=self.saveResults,
        )
        self.clear_button = customQT.createQPushButton(
            "Clear calibration test",
            QssLabels.CRITICAL_CONTROL_PANEL_BTN,
            enabled=False,
            # connect_fn=self.clearValues,
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
        self.measurements_widget = QtWidgets.QTableWidget(0, 9)
        self.measurements_widget.setHorizontalHeaderLabels(
            [
                "\u0394l x",
                "\u0394l y",
                "\u0394l z",
                "Test X mean",
                "Test Y mean",
                "Test Z mean",
                "Max sensor mean",
                "Max sensor STD",
                "Measurements",
            ]
        )
        self.measurements_widget.verticalHeader().setVisible(False)
        self.measurements_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )

        # - Measure control buttons
        hbox_measure_btns_layout = QtWidgets.QHBoxLayout()
        # vbox_distance_grid = QtWidgets.QVBoxLayout()
        distance_info_label = customQT.createLabelBox(
            "Distances from the center of the platform."
            + "\nCheck platform layout on the left."
            + "\nNOTE: \u0394l z = 0mm on top platform surface.",
            QssLabels.STATUS_LABEL_INFO,
        )
        grid_distance_spinboxes_layout = QtWidgets.QGridLayout()
        self.distance_delta_x = QtWidgets.QSpinBox()
        self.distance_delta_x.setMaximum(300)
        self.distance_delta_x.setMinimum(-300)
        self.distance_delta_y = QtWidgets.QSpinBox()
        self.distance_delta_y.setMaximum(200)
        self.distance_delta_y.setMinimum(-200)
        self.distance_delta_z = QtWidgets.QSpinBox()
        self.distance_delta_z.setMaximum(500)
        grid_distance_spinboxes_layout.addWidget(
            QtWidgets.QLabel("\u0394l x"), 0, 0, QtCore.Qt.AlignRight
        )
        grid_distance_spinboxes_layout.addWidget(
            QtWidgets.QLabel("\u0394l y"), 1, 0, QtCore.Qt.AlignRight
        )
        grid_distance_spinboxes_layout.addWidget(
            QtWidgets.QLabel("\u0394l z"), 2, 0, QtCore.Qt.AlignRight
        )
        grid_distance_spinboxes_layout.addWidget(self.distance_delta_x, 0, 1)
        grid_distance_spinboxes_layout.addWidget(self.distance_delta_y, 1, 1)
        grid_distance_spinboxes_layout.addWidget(self.distance_delta_z, 2, 1)
        grid_distance_spinboxes_layout.addWidget(QtWidgets.QLabel("mm"), 0, 2)
        grid_distance_spinboxes_layout.addWidget(QtWidgets.QLabel("mm"), 1, 2)
        grid_distance_spinboxes_layout.addWidget(QtWidgets.QLabel("mm"), 2, 2)
        grid_distance_spinboxes_layout.setSizeConstraint(
            QtWidgets.QGridLayout.SetFixedSize
        )
        # vbox_distance_grid.addWidget(distance_info_label)
        # vbox_distance_grid.addLayout(grid_distance_spinboxes_layout)
        grid_distance_fixedpoint_layout = QtWidgets.QVBoxLayout()
        grid_distance_fixedpoint_spinboxes_layout = QtWidgets.QGridLayout()
        self.fixedpoint_row = QtWidgets.QSpinBox()
        self.fixedpoint_row.setMaximum(11)
        self.fixedpoint_row.setMinimum(1)
        self.fixedpoint_row.setValue(6)
        self.fixedpoint_col = QtWidgets.QSpinBox()
        self.fixedpoint_col.setMaximum(5)
        self.fixedpoint_col.setMinimum(1)
        self.fixedpoint_col.setValue(3)
        self.fixedpoint_row.valueChanged.connect(self.changeFixedPoint)
        self.fixedpoint_col.valueChanged.connect(self.changeFixedPoint)
        grid_distance_fixedpoint_spinboxes_layout.addWidget(
            QtWidgets.QLabel("P row"), 0, 0, QtCore.Qt.AlignRight
        )
        grid_distance_fixedpoint_spinboxes_layout.addWidget(
            QtWidgets.QLabel("P col"), 1, 0, QtCore.Qt.AlignRight
        )
        grid_distance_fixedpoint_spinboxes_layout.addWidget(self.fixedpoint_row, 0, 1)
        grid_distance_fixedpoint_spinboxes_layout.addWidget(self.fixedpoint_col, 1, 1)
        grid_distance_fixedpoint_spinboxes_layout.addWidget(QtWidgets.QLabel(""), 0, 2)
        grid_distance_fixedpoint_spinboxes_layout.addWidget(QtWidgets.QLabel(""), 1, 2)
        grid_distance_fixedpoint_spinboxes_layout.setSizeConstraint(
            QtWidgets.QGridLayout.SetFixedSize
        )
        grid_distance_fixedpoint_layout.addWidget(
            QtWidgets.QLabel("Get a predefined XY distance from Pij")
        )
        grid_distance_fixedpoint_layout.addLayout(
            grid_distance_fixedpoint_spinboxes_layout
        )
        vbox_measure_btns_layout = QtWidgets.QVBoxLayout()
        vbox_measure_btns_layout.setAlignment(QtCore.Qt.AlignTop)
        self.auto_measure_button = customQT.createQPushButton(
            "Measure with sensor", enabled=False, connect_fn=None
        )
        self.remove_row_button = customQT.createQPushButton(
            "Remove selected row",
            QssLabels.CRITICAL_BTN,
            enabled=False,
            # connect_fn=self.removeRow,
        )
        vbox_measure_btns_layout.addWidget(self.auto_measure_button)
        vbox_measure_btns_layout.addWidget(self.remove_row_button)
        hbox_measure_btns_layout.addWidget(distance_info_label)
        hbox_measure_btns_layout.addLayout(grid_distance_spinboxes_layout)
        hbox_measure_btns_layout.addLayout(grid_distance_fixedpoint_layout)
        hbox_measure_btns_layout.addLayout(vbox_measure_btns_layout)

        # -  Results TableWidget
        self.calib_matrix_widget = QtWidgets.QTableWidget(6, 12)
        self.calib_matrix_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.calib_matrix_widget.setVerticalHeaderLabels(
            ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]
        )
        self.std_matrix_widget = QtWidgets.QTableWidget(6, 12)
        self.std_matrix_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.std_matrix_widget.setVerticalHeaderLabels(
            ["Fx", "Fy", "Fz", "Mx", "My", "Mz"]
        )
        self.generate_results_button = customQT.createQPushButton(
            "Apply calibration and generate results",
            QssLabels.CONTROL_PANEL_BTN,
            enabled=False,
            # connect_fn=self.generateResults,
        )

        self.color_matrix = [
            [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
            [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0],
            [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        ]
        self.updateTable(
            table_widget=self.calib_matrix_widget,
            color_matrix=self.color_matrix,
            color=(0, 10, 40),
        )
        self.updateTable(
            table_widget=self.std_matrix_widget,
            color_matrix=self.color_matrix,
            color=(0, 10, 40),
        )

        # - Build calibration layout
        vbox_calibration_layout.addWidget(self.measurements_widget)
        vbox_calibration_layout.addLayout(hbox_measure_btns_layout)
        vbox_calibration_layout.addWidget(QtWidgets.QLabel("Calibration matrix"))
        vbox_calibration_layout.addWidget(self.calib_matrix_widget)
        vbox_calibration_layout.addWidget(QtWidgets.QLabel("Calibration STD matrix"))
        vbox_calibration_layout.addWidget(self.std_matrix_widget)
        vbox_calibration_layout.addWidget(self.generate_results_button)

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
    def changeFixedPoint(self):
        lm, ln = 108, 30  # TODO set this distances in config
        if self.sender() is self.fixedpoint_col:
            self.distance_delta_x.setValue(
                lm
                * (
                    self.fixedpoint_col.value()
                    - ((self.fixedpoint_col.maximum() + 1) / 2)
                )
            )
            return
        if self.sender() is self.fixedpoint_row:
            self.distance_delta_y.setValue(
                ln
                * (
                    ((self.fixedpoint_row.maximum() + 1) / 2)
                    - self.fixedpoint_row.value()
                )
            )
            return

    # Widget functions

    def updateTable(
        self,
        table_widget: QtWidgets.QTableWidget,
        dataframe=None,
        color_matrix=None,
        color=(255, 255, 255),
    ):
        if dataframe is not None:
            for row in range(dataframe.shape[0]):
                for col in range(dataframe.shape[1]):
                    item = QtWidgets.QTableWidgetItem(str(dataframe.iloc[row, col]))
                    table_widget.setItem(row, col, item)

        if color_matrix is not None:
            for row in range(len(color_matrix)):
                for col in range(len(color_matrix[row])):
                    if color_matrix[row][col] == 1:
                        item = table_widget.item(row, col)
                        if item is None:
                            item = QtWidgets.QTableWidgetItem()
                            table_widget.setItem(row, col, item)
                        item.setBackground(QtGui.QColor(*color))
