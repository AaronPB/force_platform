# -*- coding: utf-8 -*-

from PySide6 import QtWidgets, QtGui, QtCore
from src.managers.sensorManager import SensorManager
from src.managers.dataManager import DataManager
from src.qtUIs.widgets import customQtLoaders as customQT
from src.handlers import Sensor, SensorGroup

from src.enums.qssLabels import QssLabels
from src.enums.uiResources import IconPaths
from src.enums.sensorTypes import STypes, SGTypes
from src.enums.plotTypes import PlotTypes
from src.enums.sensorStatus import SGStatus

from loguru import logger


_sensor_types: dict[STypes, IconPaths] = {
    STypes.SENSOR_LOADCELL: IconPaths.LOADCELL_ICON,
    STypes.SENSOR_ENCODER: IconPaths.ENCODER_ICON,
    STypes.SENSOR_IMU: IconPaths.IMU_ICON,
}
_sensor_group_types: dict[SGTypes, IconPaths] = {
    SGTypes.GROUP_DEFAULT: IconPaths.DEFAULT_GROUP_ICON,
    SGTypes.GROUP_PLATFORM: IconPaths.PLATFORM_ICON,
}


def clearWidgetsLayout(layout: QtWidgets.QBoxLayout) -> None:
    for i in reversed(range(layout.count())):
        widget = layout.itemAt(i).widget()
        if widget is not None:
            widget.deleteLater()


class SensorSettings:
    def __init__(self, sensor_manager: SensorManager):
        self.sensor_mngr = sensor_manager

    def updateLayout(
        self, hbox_layout: QtWidgets.QHBoxLayout, sensor_groups: list[SensorGroup]
    ) -> None:
        clearWidgetsLayout(hbox_layout)
        for group in sensor_groups:
            hbox_layout.addWidget(self.buildSensorGroupPanel(group))

    # Panel builders

    def buildSensorPanel(self, group_id: str, sensor: Sensor) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox_layout)
        # Build elements
        status_label = customQT.createIconLabelBox(
            sensor.getStatus().value[0], sensor.getStatus().value[1]
        )
        sensor_icon = IconPaths.GRAPH
        if sensor.getType() in _sensor_types:
            sensor_icon = _sensor_types[sensor.getType()]
        type_label = customQT.createIconLabelBox(sensor_icon, QssLabels.SENSOR)
        text = f"{sensor.getName()} \n {sensor.getProperties()}"
        sensor_checkbox = customQT.createSensorQCheckBox(
            text,
            QssLabels.SENSOR,
            enabled=sensor.getRead(),
            change_fn=self.sensor_mngr.setSensorRead,
            group_id=group_id,
            sensor_id=sensor.getID(),
        )
        # Build layout
        hbox_layout.addWidget(status_label)
        hbox_layout.addWidget(type_label)
        hbox_layout.addWidget(sensor_checkbox)
        return widget

    def buildSensorGroupPanel(self, group: SensorGroup) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox_layout)
        # Build elements
        status_label = customQT.createIconLabelBox(
            group.getStatus().value[0], group.getStatus().value[1]
        )
        group_icon = IconPaths.DEFAULT_GROUP_ICON
        if group.getType() in _sensor_group_types:
            group_icon = _sensor_group_types[group.getType()]
        type_label = customQT.createIconLabelBox(group_icon, QssLabels.SENSOR_GROUP)
        edit_btn = customQT.createIconQPushButton(
            IconPaths.SETTINGS,
            QssLabels.SENSOR_GROUP,
            enabled=True,
        )
        edit_btn.clicked.connect(
            lambda *, group_id=group.getID(): self.openSensorListWindow(group_id)
        )
        text = f"{group.getName()} \n{group.getSize()} sensors"
        group_checkbox = customQT.createSensorQCheckBox(
            text=text,
            qss_object=QssLabels.SENSOR_GROUP,
            enabled=group.getRead(),
            change_fn=self.sensor_mngr.setSensorRead,
            group_id=group.getID(),
        )
        # Build layout
        hbox_layout.addWidget(status_label)
        hbox_layout.addWidget(type_label)
        hbox_layout.addWidget(edit_btn)
        hbox_layout.addWidget(group_checkbox)
        return widget

    # Sensor buttons click actions

    @QtCore.Slot()
    def openSensorListWindow(self, group_id: str):
        group = self.sensor_mngr.getGroup(group_id)
        if group is None:
            logger.error(f"Group {group_id} does not exist!")
            return
        dialog_window = QtWidgets.QDialog()
        dialog_window.setWindowTitle(f"Sensor list of group {group.getName()}")
        general_layout = QtWidgets.QVBoxLayout()
        dialog_window.setLayout(general_layout)
        for sensor in group.getSensors().values():
            widget = self.buildSensorPanel(group.getID(), sensor)
            general_layout.addWidget(widget)
        dialog_window.setModal(True)
        dialog_window.exec_()


class SensorPlotSelector(QtWidgets.QWidget):
    def __init__(self, sensor_manager: SensorManager, data_manager: DataManager):
        self.sensor_mngr: SensorManager = sensor_manager
        self.data_mngr: DataManager = data_manager
        self.group_combo_box: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.options_selector_layout: QtWidgets.QBoxLayout = QtWidgets.QVBoxLayout()
        self.figure_layout: QtWidgets.QBoxLayout = QtWidgets.QVBoxLayout()
        self.idx1: int = 0
        self.idx2: int = 0

    def setupLayouts(
        self,
        combo_box: QtWidgets.QComboBox,
        options_selector: QtWidgets.QBoxLayout,
        figure: QtWidgets.QBoxLayout,
    ) -> None:
        self.group_combo_box = combo_box
        self.group_combo_box.currentIndexChanged.connect(self.buildOptionsLayout)
        self.options_selector_layout = options_selector
        self.figure_layout = figure

    def updateLayouts(self) -> None:
        self.setupComboBox()
        clearWidgetsLayout(self.figure_layout)

    def setIndexes(self, idx1: int, idx2: int) -> None:
        self.idx1 = idx1
        self.idx2 = idx2

    def setupComboBox(self) -> None:
        clearWidgetsLayout(self.options_selector_layout)
        for group in self.sensor_mngr.getGroups():
            if not group.getRead():
                continue
            if group.getStatus() == SGStatus.ERROR:
                continue
            icon_path = IconPaths.DEFAULT_GROUP_ICON
            if group.getType() in _sensor_group_types:
                icon_path = _sensor_group_types[group.getType()]
            self.group_combo_box.addItem(QtGui.QIcon(icon_path.value), group.getName())

    def updateSelectorLayout(self, sensor_group: SensorGroup) -> None:
        clearWidgetsLayout(self.options_selector_layout)
        for sensor in sensor_group.getAvailableSensors().values():
            if sensor.getType() == STypes.SENSOR_LOADCELL:
                widget = self.buildOptionPanel(
                    f"{sensor.getName()} Force",
                    PlotTypes.SENSOR_LOADCELL_FORCE,
                    sensor,
                )
                self.options_selector_layout.addWidget(widget)
                continue
            if sensor.getType() == STypes.SENSOR_ENCODER:
                widget = self.buildOptionPanel(
                    f"{sensor.getName()} Distance",
                    PlotTypes.SENSOR_ENCODER_DISTANCE,
                    sensor,
                )
                self.options_selector_layout.addWidget(widget)
                continue
            if sensor.getType() == STypes.SENSOR_IMU:
                angle_widget = self.buildOptionPanel(
                    f"{sensor.getName()} Angles",
                    PlotTypes.SENSOR_IMU_ANGLES,
                    sensor,
                )
                velocity_widget = self.buildOptionPanel(
                    f"{sensor.getName()} Angular velocity",
                    PlotTypes.SENSOR_IMU_VELOCITY,
                    sensor,
                )
                acceleration_widget = self.buildOptionPanel(
                    f"{sensor.getName()} Accelerations",
                    PlotTypes.SENSOR_IMU_ACCELERATION,
                    sensor,
                )
                self.options_selector_layout.addWidget(angle_widget)
                self.options_selector_layout.addWidget(velocity_widget)
                self.options_selector_layout.addWidget(acceleration_widget)

    def updateSensorFigurePlot(self, plot_type: PlotTypes, sensor: Sensor) -> None:
        clearWidgetsLayout(self.figure_layout)
        widget = self.data_mngr.getSensorPlotWidget(
            plot_type, sensor.getName(), self.idx1, self.idx2
        )
        self.figure_layout.addWidget(widget)

    # TODO WIP Merge both functions
    # Panel builders

    def buildOptionPanel(
        self, title: str, plot_type: PlotTypes, sensor: Sensor
    ) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox_layout)
        # Build elements
        type_label = customQT.createIconLabelBox(IconPaths.GRAPH, QssLabels.SENSOR)
        sensor_btn = customQT.createQPushButton(
            title=title,
            qss_object=QssLabels.SENSOR,
            enabled=True,
        )
        sensor_btn.clicked.connect(
            lambda *, plot_type=plot_type, sensor=sensor: self.updateSensorFigurePlot(
                plot_type, sensor
            )
        )
        # Build layout
        hbox_layout.addWidget(type_label)
        hbox_layout.addWidget(sensor_btn)
        return widget

    def buildSensorPanel(self, sensor: Sensor) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox_layout)
        # Build elements
        sensor_icon = IconPaths.GRAPH
        if sensor.getType() in _sensor_types:
            sensor_icon = _sensor_types[sensor.getType()]
        type_label = customQT.createIconLabelBox(sensor_icon, QssLabels.SENSOR)
        sensor_btn = customQT.createQPushButton(
            title=sensor.getName(),
            qss_object=QssLabels.SENSOR,
            enabled=True,
        )
        # Plot widget call
        if sensor.getType() == STypes.SENSOR_LOADCELL:
            sensor_btn.clicked.connect(
                lambda *, plot_type=PlotTypes.SENSOR_LOADCELL_FORCE, sensor=sensor: self.updateSensorFigurePlot(
                    plot_type, sensor
                )
            )
        elif sensor.getType() == STypes.SENSOR_ENCODER:
            sensor_btn.clicked.connect(
                lambda *, plot_type=PlotTypes.SENSOR_ENCODER_DISTANCE, sensor=sensor: self.updateSensorFigurePlot(
                    plot_type, sensor
                )
            )
        elif sensor.getType() == STypes.SENSOR_IMU:
            sensor_btn.clicked.connect(
                lambda *, sensor=sensor: self.updatePlotSelectorLayout(sensor)
            )
        # Build layout
        hbox_layout.addWidget(type_label)
        hbox_layout.addWidget(sensor_btn)
        return widget

    def buildSensorGroupPanel(self, group: SensorGroup) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox_layout)
        # Build elements
        group_icon = IconPaths.DEFAULT_GROUP_ICON
        if group.getType() in _sensor_group_types:
            group_icon = _sensor_group_types[group.getType()]
        type_label = customQT.createIconLabelBox(group_icon, QssLabels.SENSOR)
        group_btn = customQT.createQPushButton(
            title=group.getName(),
            qss_object=QssLabels.SENSOR_GROUP,
            enabled=True,
        )
        group_btn.clicked.connect(
            lambda *, group=group: self.updateSensorSelectorLayout(group)
        )
        # Build layout
        hbox_layout.addWidget(type_label)
        hbox_layout.addWidget(group_btn)
        return widget

    # Sensor buttons click actions

    @QtCore.Slot()
    def buildOptionsLayout(self, index):
        logger.debug(f"User select option {index}")
        self.updateSelectorLayout(self.sensor_mngr.getGroups()[index])
