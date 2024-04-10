# -*- coding: utf-8 -*-

from PySide6 import QtWidgets, QtGui, QtCore
from src.managers.sensorManager import SensorManager
from src.managers.dataManager import DataManager
from src.qtUIs.widgets import customQtLoaders as customQT
from src.handlers import Sensor, SensorGroup

from src.enums.qssLabels import QssLabels
from src.enums.uiResources import IconPaths
from src.enums.sensorTypes import STypes, SGTypes

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


class SensorSettings:
    def __init__(self, sensor_manager: SensorManager):
        self.sensor_mngr = sensor_manager

    def updateLayout(
        self, hbox_layout: QtWidgets.QHBoxLayout, sensor_groups: list[SensorGroup]
    ) -> None:
        # Clear layout
        for i in reversed(range(hbox_layout.count())):
            widget = hbox_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        # Add new widgets
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


# WIP
class SensorPlotSelector(QtWidgets.QWidget):
    def __init__(self, sensor_manager: SensorManager, data_manager: DataManager):
        self.sensor_mngr = sensor_manager
        self.data_mngr = data_manager

    def buildSensorGroupSelector(self, vbox_layout: QtWidgets.QVBoxLayout) -> None:
        pass

    def buildSensorSelector(self, vbox_layout: QtWidgets.QVBoxLayout) -> None:
        pass

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
        hbox_layout.addWidget(group_checkbox)
        return widget
