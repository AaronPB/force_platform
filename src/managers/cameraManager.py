# -*- coding: utf-8 -*-

from loguru import logger
from src.handlers import drivers
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorParams import SParams
from src.enums.cameraParams import CParams
from src.enums.sensorTypes import STypes
from src.qtUIs.threads.cameraThread import CameraRecordThread, Camera
from typing import Protocol

# Required param keys for camera handlers
camera_global_keys = [
    CParams.NAME,
    CParams.READ,
    CParams.CONNECTION_SECTION,
]
camera_conn_keys = [CParams.SERIAL]


class ConfigYAMLHandler(Protocol):
    def setConfigValue(self, key_path: str, value) -> None: ...

    def getConfigValue(self, key_path: str, default_value=None): ...


class CameraManager:
    def __init__(self) -> None:
        self.config_mngr: ConfigYAMLHandler
        self.camera_threads: list[CameraRecordThread] = []

    def setup(self, config_manager: ConfigYAMLHandler) -> None:
        self.config_mngr = config_manager
        config_cameras = self.config_mngr.getConfigValue(
            CfgPaths.CAMERA_SECTION.value, {}
        )
        self.clearThreads()
        self.loadCameras(config_cameras)

    def loadCameras(self, contents: dict) -> None:
        if not contents:
            logger.warning("No cameras found in config!")
            return
        for camera_id in contents:
            camera = self.loadCamera(camera_id, contents[camera_id])
            if camera is None:
                continue
            self.camera_threads.append(CameraRecordThread(camera))

    def loadCamera(self, id: str, params: dict) -> Camera:
        if not all(key.value in params.keys() for key in camera_global_keys):
            logger.warning(f"Camera {id} does not have the required keys! Not loaded.")
            return None
        if not all(
            key.value in params[CParams.CONNECTION_SECTION.value].keys()
            for key in camera_conn_keys
        ):
            logger.warning(
                f"Camera {id} does not have the required connection keys! Not loaded."
            )
            return None
        camera = Camera()
        camera.setup(id, params)
        return camera

    def clearThreads(self) -> None:
        for thread in self.camera_threads:
            if thread.isRunning():
                thread.stop()
        self.camera_threads.clear()

    # Setters and getters

    def setCameraRead(self, read: bool, camera_id: str) -> None:
        for thread in self.camera_threads:
            camera = thread.getCamera()
            if camera.getID() != camera_id:
                continue
            logger.debug(f"Set read status of camera {camera_id} to {read}")
            camera.setRead(read)
            self.config_mngr.setConfigValue(
                CfgPaths.CAMERA_SECTION.value
                + "."
                + camera_id
                + "."
                + CParams.READ.value,
                read,
            )
            return

    def getCameras(self) -> list[Camera]:
        return [thread.getCamera() for thread in self.camera_threads]

    def getCameraThreads(self) -> list[CameraRecordThread]:
        return self.camera_threads
