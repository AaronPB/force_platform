# -*- coding: utf-8 -*-

from PySide6 import QtCore
from src.handlers.camera import Camera


class CameraRecordThread(QtCore.QThread):
    def __init__(self, camera: Camera) -> None:
        super().__init__()
        self.camera = camera
        self.file_path = "output.avi"

    def run(self) -> None:
        self.camera.connect(file_path=self.file_path)

    def stop(self) -> None:
        self.camera.disconnect()

    def setFilePath(self, file_path: str) -> None:
        self.file_path = file_path
