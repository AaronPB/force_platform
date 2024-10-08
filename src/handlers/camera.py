# -*- coding: utf-8 -*-

from loguru import logger
import cv2
from src.enums.cameraStatus import CStatus
from src.enums.cameraParams import CParams


class Camera:
    def __init__(self) -> None:
        self.id: str
        self.params: dict
        self.status: CStatus = CStatus.IGNORED
        self.recording: bool = False
        self.camera: cv2.VideoCapture
        self.video_output: cv2.VideoWriter

    def setup(self, id: str, params: dict) -> None:
        self.id = id
        self.params = params

    def connect(self, check: bool = False, file_path: str = None) -> bool:
        if not self.params[CParams.READ.value]:
            self.status = CStatus.IGNORED
            return False
        if not check and self.status is not CStatus.AVAILABLE:
            return False
        self.status = CStatus.NOT_FOUND
        if self.record(check, file_path):
            self.status = CStatus.AVAILABLE
            return True
        return False

    def record(self, check: bool = False, file_path: str = None) -> bool:
        usb_path = self.params[CParams.CONNECTION_SECTION.value][CParams.SERIAL.value]
        self.camera = cv2.VideoCapture(usb_path)
        # Get camera props
        frame_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = self.camera.get(cv2.CAP_PROP_FPS)
        # Update camera props in case user has defined them in config via settings
        # FIXME OpenCV could override camera values, and the FPS drops significantly.
        if CParams.SETTINGS_SECTION.value in self.params:
            camera_settings: dict = self.params[CParams.SETTINGS_SECTION.value]
            self.camera.set(
                cv2.CAP_PROP_FRAME_WIDTH,
                camera_settings.get(CParams.FRAME_WIDTH.value, frame_width),
            )
            self.camera.set(
                cv2.CAP_PROP_FRAME_HEIGHT,
                camera_settings.get(CParams.FRAME_HEIGHT.value, frame_height),
            )
            self.camera.set(
                cv2.CAP_PROP_FPS, camera_settings.get(CParams.FPS.value, fps)
            )
            # Update camera props
            frame_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = self.camera.get(cv2.CAP_PROP_FPS)
        if not self.camera.isOpened():
            self.camera.release()
            logger.warning(f"Could not connect or open camera port {usb_path}")
            return False
        if check:
            self.camera.release()
            return True

        # Start camera recording
        logger.debug(
            "Camera props" + f"\nFRAME: {frame_width}x{frame_height}" + f"\nFPS: {fps}"
        )
        self.recording = True
        if file_path is None:
            file_path = "output.avi"
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        logger.info(
            f"Recording camera {self.params[CParams.NAME.value]} to file path {file_path}"
        )
        self.video_output = cv2.VideoWriter(
            file_path, fourcc, fps, (frame_width, frame_height)
        )
        while self.recording:
            ret, frame = self.camera.read()
            if not ret:
                break
            self.video_output.write(frame)
        return True

    def disconnect(self) -> None:
        self.recording = False
        if self.camera is not None:
            self.camera.release()
        if self.video_output is not None:
            self.video_output.release()
        logger.info(f"Stopped recording of camera {self.params[CParams.NAME.value]}")

    # Setters and getters methods

    def setRead(self, read: bool) -> None:
        self.params[CParams.READ.value] = read

    def getID(self) -> str:
        return self.id

    def getName(self) -> str:
        return self.params[CParams.NAME.value]

    def getRead(self) -> bool:
        return self.params[CParams.READ.value]

    def getStatus(self) -> CStatus:
        return self.status

    def getProperties(self) -> str:
        text = " - "
        for property in self.params[CParams.PROPERTIES_SECTION.value]:
            text = (
                text + self.params[CParams.PROPERTIES_SECTION.value][property] + " - "
            )
        return text
