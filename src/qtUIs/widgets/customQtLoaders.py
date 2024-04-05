# -*- coding: utf-8 -*-

from src.enums.qssLabels import QssLabels
from PySide6 import QtWidgets, QtGui


def createIconLabelBox(
    icon: QtGui.QPixmap, qss_object: QssLabels = None
) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel()
    label.setPixmap(icon)
    if qss_object is not None:
        label.setObjectName(qss_object.value)
    return label


def createLabelBox(text: str, qss_object: QssLabels = None) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel(text)
    if qss_object is not None:
        label.setObjectName(qss_object.value)
    return label


def createQPushButton(
    title: str,
    qss_object: QssLabels = None,
    enabled: bool = False,
    icon: QtGui.QIcon = None,
    connect_fn=None,
) -> QtWidgets.QPushButton:
    button = QtWidgets.QPushButton(title)
    if qss_object is not None:
        button.setObjectName(qss_object.value)
    button.setEnabled(enabled)
    if icon is not None:
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
    enabled: bool = True,
    change_fn=None,
    index=0,
) -> QtWidgets.QCheckBox:
    checkbox = QtWidgets.QCheckBox(text)
    if qss_object is not None:
        checkbox.setObjectName(qss_object.value)
    checkbox.setEnabled(enabled)
    if change_fn is not None:
        checkbox.stateChanged.connect(
            lambda state, index=index: change_fn(index, state == 2)
        )
    return checkbox
