# -*- coding: utf-8 -*-

from PySide6 import QtWidgets, QtGui, QtCore
from src.managers.sensorManager import SensorManager
from src.managers.cameraManager import CameraManager
from src.managers.dataManager import DataManager
from src.qtUIs.widgets import customQtLoaders as customQT
from src.handlers import Sensor, SensorGroup
from src.handlers.camera import Camera

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


class CameraSettings:
    def __init__(self, camera_manager: CameraManager):
        self.camera_mngr = camera_manager

    def updateLayout(
        self, hbox_layout: QtWidgets.QHBoxLayout, camera_list: list[Camera]
    ) -> None:
        clearWidgetsLayout(hbox_layout)
        for camera in camera_list:
            hbox_layout.addWidget(self.buildCameraPanel(camera))

    # Panel builders

    def buildCameraPanel(self, camera: Camera) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox_layout)
        # Build elements
        status_label = customQT.createIconLabelBox(
            camera.getStatus().value[0], camera.getStatus().value[1]
        )
        type_label = customQT.createIconLabelBox(
            IconPaths.CAMERA_ICON, QssLabels.SENSOR_GROUP
        )
        text = f"{camera.getName()} \n {camera.getProperties()}"
        sensor_checkbox = customQT.createCameraQCheckBox(
            text,
            QssLabels.SENSOR_GROUP,
            enabled=camera.getRead(),
            change_fn=self.camera_mngr.setCameraRead,
            sensor_id=camera.getID(),
        )
        # Build layout
        hbox_layout.addWidget(status_label)
        hbox_layout.addWidget(type_label)
        hbox_layout.addWidget(sensor_checkbox)
        return widget


class PreviewPlotSelector(QtWidgets.QWidget):
    def __init__(self, data_manager: DataManager):
        self.data_mngr: DataManager = data_manager
        self.combo_box: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.figure_layout: QtWidgets.QBoxLayout = QtWidgets.QVBoxLayout()
        self.idx1: int = 0
        self.idx2: int = 0

    def setupLayouts(
        self,
        combo_box: QtWidgets.QComboBox,
        figure: QtWidgets.QBoxLayout,
    ) -> None:
        self.combo_box = combo_box
        self.combo_box.currentTextChanged.connect(self.buildPlotPreview)
        self.figure_layout = figure

    def updateLayouts(self) -> None:
        self.setupComboBox()

    def updatePreview(self, idx1: int, idx2: int) -> None:
        self.idx1 = idx1
        self.idx2 = idx2
        self.updateSensorFigurePlot(self.combo_box.currentText())

    def setupComboBox(self) -> None:
        self.combo_box.clear()
        data_keys = self.data_mngr.getCalibrateDataframe().to_dict().keys()
        # Avoid timestamp in combo box options
        data_iterator = iter(data_keys)
        next(data_iterator)
        for key in data_iterator:
            self.combo_box.addItem(key)

    def updateSensorFigurePlot(self, sensor_name: str) -> None:
        clearWidgetsLayout(self.figure_layout)
        widget = self.data_mngr.getPlotPreviewWidget(sensor_name, self.idx1, self.idx2)
        self.figure_layout.addWidget(widget)

    # Sensor buttons click actions

    @QtCore.Slot()
    def buildPlotPreview(self, option):
        if not option:
            return
        logger.debug(f"User select option {option}")
        self.updateSensorFigurePlot(option)


class SensorPlotSelector(QtWidgets.QWidget):
    def __init__(self, data_manager: DataManager):
        self.data_mngr: DataManager = data_manager
        self.group_combo_box: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.options_selector_layout: QtWidgets.QBoxLayout = QtWidgets.QVBoxLayout()
        self.figure_layout: QtWidgets.QBoxLayout = QtWidgets.QVBoxLayout()
        self.group_list: list[SensorGroup] = []
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

    def updateLayouts(self, group_list: list[SensorGroup]) -> None:
        self.group_list = group_list
        self.setupComboBox()
        clearWidgetsLayout(self.figure_layout)

    def setIndexes(self, idx1: int, idx2: int) -> None:
        self.idx1 = idx1
        self.idx2 = idx2

    def setupComboBox(self) -> None:
        self.group_combo_box.clear()
        clearWidgetsLayout(self.options_selector_layout)
        for group in self.group_list:
            icon_path = IconPaths.DEFAULT_GROUP_ICON
            if group.getType() in _sensor_group_types:
                icon_path = _sensor_group_types[group.getType()]
            self.group_combo_box.addItem(QtGui.QIcon(icon_path.value), group.getName())

    def updateSelectorLayout(self, sensor_group: SensorGroup) -> None:
        clearWidgetsLayout(self.options_selector_layout)
        for sensor in sensor_group.getSensors(only_available=True).values():
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

    # Panel builders

    def buildOptionPanel(
        self, title: str, plot_type: PlotTypes, sensor: Sensor
    ) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox_layout)
        # Build elements
        sensor_icon = IconPaths.GRAPH
        if sensor.getType() in _sensor_types:
            sensor_icon = _sensor_types[sensor.getType()]
        type_label = customQT.createIconLabelBox(sensor_icon, QssLabels.SENSOR)
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

    # Sensor buttons click actions

    @QtCore.Slot()
    def buildOptionsLayout(self, index):
        if index == -1:
            return
        logger.debug(f"User select option {index}")
        self.updateSelectorLayout(self.group_list[index])


class PlatformPlotSelector(QtWidgets.QWidget):
    def __init__(self, data_manager: DataManager):
        self.data_mngr: DataManager = data_manager
        self.group_combo_box: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.options_selector_layout: QtWidgets.QBoxLayout = QtWidgets.QVBoxLayout()
        self.figure_layout: QtWidgets.QBoxLayout = QtWidgets.QVBoxLayout()
        self.group_list: list[SensorGroup] = []
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

    def updateLayouts(self, group_list: list[SensorGroup]) -> None:
        self.group_list = group_list
        self.setupComboBox()
        clearWidgetsLayout(self.figure_layout)

    def setIndexes(self, idx1: int, idx2: int) -> None:
        self.idx1 = idx1
        self.idx2 = idx2

    def setupComboBox(self) -> None:
        self.group_combo_box.clear()
        clearWidgetsLayout(self.options_selector_layout)
        for group in self.group_list:
            self.group_combo_box.addItem(
                QtGui.QIcon(IconPaths.PLATFORM_ICON.value), group.getName()
            )

    def updateSelectorLayout(self, sensor_group: SensorGroup) -> None:
        clearWidgetsLayout(self.options_selector_layout)
        sensor_list = [
            sensor.getName()
            for sensor in sensor_group.getSensors(
                only_available=True, sensor_type=STypes.SENSOR_LOADCELL
            ).values()
        ]
        forces_widget = self.buildOptionPanel(
            "Total forces", PlotTypes.GROUP_PLATFORM_FORCES, sensor_list, False
        )
        if len(sensor_list) > 0 and len(sensor_list) <= 12:
            forces_widget = self.buildOptionPanel(
                "Total forces", PlotTypes.GROUP_PLATFORM_FORCES, sensor_list
            )
        cop_widget = self.buildOptionPanel(
            "Platform COP", PlotTypes.GROUP_PLATFORM_COP, sensor_list, False
        )
        if len(sensor_list) == 12:
            cop_widget = self.buildOptionPanel(
                "Platform COP", PlotTypes.GROUP_PLATFORM_COP, sensor_list
            )
        self.options_selector_layout.addWidget(forces_widget)
        self.options_selector_layout.addWidget(cop_widget)

    def updateSensorFigurePlot(
        self, plot_type: PlotTypes, sensor_list: list[str]
    ) -> None:
        clearWidgetsLayout(self.figure_layout)
        widget = self.data_mngr.getGroupPlotWidget(
            plot_type, sensor_list, self.idx1, self.idx2
        )
        self.figure_layout.addWidget(widget)

    # Panel builders

    def buildOptionPanel(
        self,
        title: str,
        plot_type: PlotTypes,
        sensor_list: list[str],
        enable: bool = True,
    ) -> QtWidgets.QWidget:
        widget = QtWidgets.QWidget()
        hbox_layout = QtWidgets.QHBoxLayout()
        widget.setLayout(hbox_layout)
        # Build elements
        type_label = customQT.createIconLabelBox(IconPaths.GRAPH, QssLabels.SENSOR)
        sensor_btn = customQT.createQPushButton(
            title=title,
            qss_object=QssLabels.SENSOR,
            enabled=enable,
        )
        sensor_btn.clicked.connect(
            lambda *, plot_type=plot_type, sensor_list=sensor_list: self.updateSensorFigurePlot(
                plot_type, sensor_list
            )
        )
        # Build layout
        hbox_layout.addWidget(type_label)
        hbox_layout.addWidget(sensor_btn)
        return widget

    # Sensor buttons click actions

    @QtCore.Slot()
    def buildOptionsLayout(self, index):
        if index == -1:
            return
        logger.debug(f"User select option {index}")
        self.updateSelectorLayout(self.group_list[index])


class CalibrationSelector(QtWidgets.QWidget):
    def __init__(self):
        self.group_combo_box: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.sensor_combo_box: QtWidgets.QComboBox = QtWidgets.QComboBox()
        self.group_list: list[SensorGroup] = []

    def setupLayouts(
        self,
        group_combo_box: QtWidgets.QComboBox,
        sensor_combo_box: QtWidgets.QComboBox,
    ) -> None:
        self.group_combo_box = group_combo_box
        self.group_combo_box.currentIndexChanged.connect(self.buildSensorComboBox)
        self.sensor_combo_box = sensor_combo_box

    def updateLayouts(self, group_list: list[SensorGroup]) -> None:
        self.group_list = group_list
        self.setupGroupComboBox()

    def setupGroupComboBox(self) -> None:
        self.group_combo_box.clear()
        for group in self.group_list:
            if group.getStatus() is not SGStatus.OK:
                continue
            self.group_combo_box.addItem(
                QtGui.QIcon(IconPaths.PLATFORM_ICON.value), group.getName()
            )

    def setupSensorComboBox(self, sensor_group: SensorGroup) -> None:
        self.sensor_combo_box.clear()
        for sensor in sensor_group.getSensors(
            only_available=True, sensor_type=STypes.SENSOR_LOADCELL
        ).values():
            self.sensor_combo_box.addItem(
                QtGui.QIcon(IconPaths.LOADCELL_ICON.value), sensor.getName()
            )

    # Sensor buttons click actions

    @QtCore.Slot()
    def buildSensorComboBox(self, index):
        if index == -1:
            return
        logger.debug(f"User select option {index}")
        self.setupSensorComboBox(self.group_list[index])

    # Getters

    def getSelectedGroup(self) -> SensorGroup:
        index = self.group_combo_box.currentIndex()
        return self.group_list[index]

    def getSelectedSensor(self) -> Sensor | None:
        group_index = self.group_combo_box.currentIndex()
        sensor_name = self.sensor_combo_box.currentText()
        group = self.group_list[group_index]
        selected_sensor = None
        for sensor in group.getSensors(
            only_available=True, sensor_type=STypes.SENSOR_LOADCELL
        ).values():
            if sensor.getName() == sensor_name:
                selected_sensor = sensor
                break
        return selected_sensor
