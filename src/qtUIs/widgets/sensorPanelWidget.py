# -*- coding: utf-8 -*-

from loguru import logger
from src.enums.qssLabels import QssLabels
from src.enums.uiResources import IconPaths
from PySide6 import QtWidgets, QtGui, QtCore
from src.qtUIs.widgets import customQtLoaders
from src.managers.sensorManager import SensorManager
from src.handlers import Sensor, SensorGroup


class SensorPanelWidget:
    def __init__(self, sensor_manager: SensorManager):
        self.sensor_mngr = sensor_manager

    # Panel list getters

    def getSensorListPanel(self, group_id: str) -> list[QtWidgets.QWidget]:
        panel_list: list[QtWidgets.QWidget] = []
        sensor_group = self.sensor_mngr.getGroup(group_id)
        for sensor in sensor_group.getSensors().values():
            widget = self.buildSensorPanel(sensor_group.getID(), sensor)
            panel_list.append(widget)
        return panel_list

    def getSensorGroupPlatformPanels(self) -> list[QtWidgets.QWidget]:
        panel_list: list[QtWidgets.QWidget] = []
        for group in self.sensor_mngr.getPlatformGroups():
            widget = self.buildSensorGroupPanel(group)
            panel_list.append(widget)
        return panel_list

    def getSensorGroupDefaultPanels(self) -> list[QtWidgets.QWidget]:
        panel_list: list[QtWidgets.QWidget] = []
        for group in self.sensor_mngr.getDefaultGroups():
            widget = self.buildSensorGroupPanel(group)
            panel_list.append(widget)
        return panel_list

    # Panel builders

    def buildSensorPanel(self, group_id: str, sensor: Sensor) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox_layout)
        # Build elements
        # TODO Change icons and colors based on current status
        status_label = customQtLoaders.createIconLabelBox(
            sensor.getStatus().value[0], sensor.getStatus().value[1]
        )
        type_label = customQtLoaders.createIconLabelBox(
            IconPaths.GRAPH, QssLabels.SENSOR
        )
        text = f"{sensor.getName()} \n {sensor.getProperties()}"
        sensor_checkbox = customQtLoaders.createSensorQCheckBox(
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
        # TODO Change icons and colors based on current status
        status_label = customQtLoaders.createIconLabelBox(
            group.getStatus().value[0], group.getStatus().value[1]
        )
        edit_btn = customQtLoaders.createIconQPushButton(
            IconPaths.SETTINGS,
            QssLabels.SENSOR_GROUP,
            enabled=True,
        )
        edit_btn.clicked.connect(
            lambda *, group_id=group.getID(): self.openSensorListWindow(group_id)
        )
        text = f"{group.getName()} \n{group.getSize()} sensors"
        group_checkbox = customQtLoaders.createSensorQCheckBox(
            text=text,
            qss_object=QssLabels.SENSOR_GROUP,
            enabled=group.getRead(),
            change_fn=self.sensor_mngr.setSensorRead,
            group_id=group.getID(),
        )
        # Build layout
        hbox_layout.addWidget(status_label)
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
