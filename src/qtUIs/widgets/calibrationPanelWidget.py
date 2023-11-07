# -*- coding: utf-8 -*-

from PySide6 import QtWidgets, QtGui, QtCore
from src.enums.qssLabels import QssLabels
from src.managers.calibrationManager import CalibrationManager
from src.qtUIs.widgets.matplotlibWidgets import PlotRegressionWidget


class CalibrationPanelWidget(QtWidgets.QWidget):
    def __init__(self, calib_mngr: CalibrationManager):
        super(CalibrationPanelWidget, self).__init__()
        self.calib_mngr = calib_mngr

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

    def loadLayout(self) -> QtWidgets.QVBoxLayout:
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setAlignment(QtCore.Qt.AlignTop)

        # Sensor info
        group_box_sensor_info = QtWidgets.QGroupBox("Sensor information")
        self.vbox_sensor_info_layout = QtWidgets.QVBoxLayout()
        self.vbox_sensor_info_layout.setAlignment(QtCore.Qt.AlignTop)
        group_box_sensor_info.setLayout(self.vbox_sensor_info_layout)
        self.sensor_info_label = self.createLabelBox(
            "Select an available sensor", QssLabels.STATUS_LABEL_WARN
        )
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

        # - Measure control buttons
        grid_measure_btns_layout = QtWidgets.QGridLayout()
        self.auto_measure_button = self.createQPushButton(
            "Measure with sensor", enabled=False
        )
        self.manual_measure_button = self.createQPushButton(
            "Measure with value", enabled=False
        )
        self.test_value_input = QtWidgets.QLineEdit()
        self.test_value_input.setPlaceholderText(
            "Enter calibration value: (example) 14.67"
        )
        self.test_value_input.setDisabled(True)
        grid_measure_btns_layout.addWidget(self.auto_measure_button, 0, 0)
        grid_measure_btns_layout.addWidget(self.manual_measure_button, 0, 1)
        grid_measure_btns_layout.addWidget(self.test_value_input, 0, 2)

        # - TableWidget for results
        self.calib_results_widget = QtWidgets.QTableWidget()
        self.calib_results_widget.setRowCount(3)
        self.calib_results_widget.setColumnCount(1)
        self.calib_results_widget.setVerticalHeaderLabels(
            ["Scope (m)", "Intercept (b)", "Score (r2)"]
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

        # - Build calibration layout
        vbox_calibration_layout.addWidget(self.data_tree_widget)
        vbox_calibration_layout.addLayout(grid_measure_btns_layout)
        vbox_calibration_layout.addWidget(self.calib_results_widget)
        vbox_calibration_layout.addWidget(self.plot_widget)

        # Results handler buttons
        grid_results_btns_layout = QtWidgets.QGridLayout()
        self.save_button = self.createQPushButton(
            "Save results", QssLabels.CONTROL_PANEL_BTN, enabled=False
        )
        self.clear_button = self.createQPushButton(
            "Clear calibration test",
            QssLabels.CRITICAL_CONTROL_PANEL_BTN,
            enabled=False,
        )
        grid_results_btns_layout.addWidget(self.save_button, 0, 0)
        grid_results_btns_layout.addWidget(self.clear_button, 0, 2)

        # Build main layout
        main_layout.addWidget(group_box_sensor_info)
        main_layout.addItem(QtWidgets.QSpacerItem(10, 10))
        main_layout.addWidget(group_box_calibration)
        main_layout.addItem(
            QtWidgets.QSpacerItem(
                20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
            )
        )
        main_layout.addLayout(grid_results_btns_layout)

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
