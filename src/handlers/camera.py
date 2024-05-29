# -*- coding: utf-8 -*-

from loguru import logger
import cv2
from src.enums.sensorStatus import SStatus
from src.enums.cameraParams import CParams


class Camera:
    def __init__(self) -> None:
        self.id: str
        self.params: dict
        self.status: SStatus
        self.recording: bool = False
        self.camera: cv2.VideoCapture
        self.video_output: cv2.VideoWriter

    def setup(self, id: str, params: dict) -> None:
        self.id = id
        self.params = params

    def connect(self, check: bool = False, file_path: str = None) -> bool:
        if not self.params[CParams.READ.value]:
            self.status = SStatus.IGNORED
            return False
        if not check and self.status is not SStatus.AVAILABLE:
            return False
        self.status = SStatus.NOT_FOUND
        if self.record(check, file_path):
            self.status = SStatus.AVAILABLE
            return True
        return False

    def record(self, check: bool = False, file_path: str = None) -> bool:
        usb_path = self.params[CParams.CONNECTION_SECTION.value][CParams.SERIAL.value]
        self.camera = cv2.VideoCapture(usb_path)
        if not self.camera.isOpened():
            self.camera.release()
            logger.warning(f"Could not connect or open camera port {usb_path}")
            return False
        if check:
            self.camera.release()
            return True

        # Start camera recording
        self.recording = True
        if file_path is None:
            file_path = "output.avi"
        fourcc = cv2.VideoWriter_fourcc(*"XVID")
        frame_width = int(self.camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # fps = self.camera.get(cv2.CAP_PROP_FPS) If you want to take native fps
        fps = self.params[CParams.SETTINGS_SECTION.value][CParams.FPS.value]
        logger.info(
            f"Recording camera {self.params[CParams.NAME.value]} to file path {file_path}"
        )
        self.video_output = cv2.VideoWriter(
            file_path, fourcc, fps, frame_width, frame_height
        )
        while self.recording:
            ret, frame = self.camera.read()
            if not ret:
                break
            self.video_output.write(frame)
            cv2.imshow("Recording", frame)
        return True

    def disconnect(self) -> None:
        self.recording = False
        if self.camera is not None:
            self.camera.release()
        if self.video_output is not None:
            self.video_output.release()
        cv2.destroyAllWindows()
        logger.info(f"Stopped recording of camera {self.params[CParams.NAME.value]}")
