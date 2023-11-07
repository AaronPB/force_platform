# -*- coding: utf-8 -*-

from PySide6 import QtWidgets, QtGui, QtCore
from src.managers.calibrationManager import CalibrationManager


class CalibrationPanelWidget(QtWidgets.QWidget):
    def __init__(self, calib_mngr: CalibrationManager):
        super(CalibrationPanelWidget, self).__init__()
        self.calib_mngr = calib_mngr

        self.setLayout(self.loadLayout())

    def loadLayout(self) -> QtWidgets.QVBoxLayout:
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        # Sensor info
        group_box_sensor_info = QtWidgets.QGroupBox("Sensor information")
        self.vbox_sensor_info_layout = QtWidgets.QVBoxLayout()
        self.vbox_sensor_info_layout.setAlignment(QtCore.Qt.AlignTop)
        group_box_sensor_info.setLayout(self.vbox_sensor_info_layout)
        self.sensor_info_label = QtWidgets.QLabel("Select an available sensor")
        self.vbox_sensor_info_layout.addWidget(self.sensor_info_label)

        # Calibration info
        group_box_calibration = QtWidgets.QGroupBox("Measurements for calibration")
        vbox_calibration_layout = QtWidgets.QVBoxLayout()
        vbox_calibration_layout.setAlignment(QtCore.Qt.AlignTop)
        group_box_calibration.setLayout(vbox_calibration_layout)

        # - TreeWidget for measurements
        self.data_tree_widget = QtWidgets.QTreeWidget()
        self.data_tree_widget.setHeaderLabels(
            ["Test value", "Sensor mean", "Sensor STD", "Num. of measurements"]
        )
        self.data_tree_widget.header().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        for column in range(self.data_tree_widget.columnCount()):
            self.data_tree_widget.headerItem().setTextAlignment(
                column, QtCore.Qt.AlignCenter
            )

        # - TableWidget for results
        self.calib_results_widget = QtWidgets.QTableWidget()
        self.calib_results_widget.setRowCount(3)
        self.calib_results_widget.setColumnCount(1)
        self.calib_results_list = []
        self.calib_results_widget.setVerticalHeaderLabels(
            ["Scope (m)", "Intercept (b)", "Score (r2)"]
        )
        self.calib_results_widget.horizontalHeader().setVisible(False)
        self.calib_results_widget.horizontalHeader().setSectionResizeMode(
            QtWidgets.QHeaderView.Stretch
        )
        self.scope_result_label = QtWidgets.QLabel("0")
        self.intercept_result_label = QtWidgets.QLabel("0")
        self.score_result_label = QtWidgets.QLabel("0")
        self.calib_results_widget.setCellWidget(0, 0, self.scope_result_label)
        self.calib_results_widget.setCellWidget(1, 0, self.intercept_result_label)
        self.calib_results_widget.setCellWidget(2, 0, self.score_result_label)

        # - TODO PlotWidget to plot measurements

        # - Build calibration layout
        vbox_calibration_layout.addWidget(self.data_tree_widget)
        vbox_calibration_layout.addWidget(self.calib_results_widget)

        # Build main layout
        main_layout.addWidget(group_box_sensor_info)
        main_layout.addItem(QtWidgets.QSpacerItem(20, 20))
        main_layout.addWidget(group_box_calibration)

        return main_layout

    # UI buttons click connectors

    @QtCore.Slot()
    def recordData(self):
        pass

    @QtCore.Slot()
    def recordDataWithCalib(self):
        pass

    # Widget functions

    def loadSensor(self):
        pass
