# -*- coding: utf-8 -*-

from src.enums.qssLabels import QssLabels
from src.enums.uiResources import IconPaths
from PySide6 import QtWidgets, QtGui, QtCore


def createIconLabelBox(
    icon_path: IconPaths, qss_object: QssLabels = None
) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel()
    icon = QtGui.QPixmap(icon_path.value)
    label.setPixmap(icon)
    label.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
    )
    if qss_object is not None:
        label.setObjectName(qss_object.value)
    return label


def createLabelBox(text: str, qss_object: QssLabels = None) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel(text)
    if qss_object is not None:
        label.setObjectName(qss_object.value)
    return label


def createIconQPushButton(
    icon_path: IconPaths,
    qss_object: QssLabels = None,
    enabled: bool = False,
    connect_fn=None,
) -> QtWidgets.QPushButton:
    button = QtWidgets.QPushButton()
    icon = QtGui.QIcon(icon_path.value)
    button.setIcon(icon)
    button.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Preferred
    )
    button.setCursor(QtCore.Qt.PointingHandCursor)
    if qss_object is not None:
        button.setObjectName(qss_object.value)
    button.setEnabled(enabled)
    if connect_fn is not None:
        button.clicked.connect(connect_fn)
    return button


def createQPushButton(
    title: str,
    qss_object: QssLabels = None,
    enabled: bool = False,
    icon_path: IconPaths = None,
    connect_fn=None,
) -> QtWidgets.QPushButton:
    button = QtWidgets.QPushButton(title)
    button.setCursor(QtCore.Qt.PointingHandCursor)
    if qss_object is not None:
        button.setObjectName(qss_object.value)
    button.setEnabled(enabled)
    if icon_path is not None:
        icon = QtGui.QIcon(icon_path.value)
        button.setIcon(icon)
    if connect_fn is not None:
        button.clicked.connect(connect_fn)
    return button


def createSensorQPushButton(
    title: str,
    qss_object: QssLabels = None,
    connect_fn=None,
    index: int = 0,
    platform: int = 1,
) -> QtWidgets.QPushButton:
    button = QtWidgets.QPushButton(title)
    button.setEnabled(False)
    if qss_object is not None:
        button.setObjectName(qss_object.value)
        button.setEnabled(qss_object == QssLabels.SENSOR_CONNECTED)
    if connect_fn is not None:
        button.clicked.connect(
            lambda index=index, platform=platform: connect_fn(index, platform)
        )
    return button


def createSensorQCheckBox(
    text: str,
    qss_object: QssLabels = None,
    enabled: bool = False,
    change_fn=None,
    group_id: str = None,
    sensor_id: str = None,
) -> QtWidgets.QCheckBox:
    checkbox = QtWidgets.QCheckBox(text)
    checkbox.setSizePolicy(
        QtWidgets.QSizePolicy.Policy.Preferred, QtWidgets.QSizePolicy.Policy.Preferred
    )
    checkbox.setCursor(QtCore.Qt.PointingHandCursor)
    if qss_object is not None:
        checkbox.setObjectName(qss_object.value)
    checkbox.setChecked(enabled)
    if change_fn is not None and group_id is not None:
        checkbox.stateChanged.connect(
            lambda state, group_id=group_id, sensor_id=sensor_id: change_fn(
                state == 2, group_id, sensor_id
            )
        )
    return checkbox
