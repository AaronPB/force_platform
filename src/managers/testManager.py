# -*- coding: utf-8 -*-

import time
from loguru import logger
from src.handlers.sensorGroup import SensorGroup
# from src.qtUIs.threads.cameraThread import CameraRecordThread


class TestManager:
    __test__ = False

    def __init__(self) -> None:
        self.sensor_groups: list[SensorGroup]
        # self.camera_threads: list[CameraRecordThread] = []
        self.sensors_connected: bool = False
        self.test_times: list = []

    # Setters and getters
    def setSensorGroups(self, sensor_groups: list[SensorGroup]) -> None:
        self.sensor_groups = sensor_groups

    # def setCameraThreads(self, camera_threads: list[CameraRecordThread]) -> None:
    #     self.camera_threads = camera_threads

    def getSensorConnected(self) -> bool:
        return self.sensors_connected

    def getTestTimes(self) -> list:
        return self.test_times

    # Test methods
    def checkConnection(self) -> bool:
        connection_results_list = [
            handler.checkConnections() for handler in self.sensor_groups
        ]
        # [thread.getCamera().connect(check=True) for thread in self.camera_threads]
        self.sensors_connected = any(connection_results_list)
        return self.sensors_connected

    def testStart(self, test_folder_path: str, test_name: str) -> None:
        logger.info(f"Starting test: {test_name}")
        self.test_times.clear()
        [handler.clearValues() for handler in self.sensor_groups]
        [handler.start() for handler in self.sensor_groups]
        # for thread in self.camera_threads:
        #     thread.setFilePath(test_folder_path + "/" + test_name)
        #     thread.start()

    def testRegisterValues(self) -> None:
        self.test_times.append(round(time.time() * 1000))
        [handler.register() for handler in self.sensor_groups]

    def testStop(self, test_name: str) -> None:
        logger.info(f"Finish test: {test_name}")
        [handler.stop() for handler in self.sensor_groups]
        # for thread in self.camera_threads:
        #     if thread.isRunning():
        #         thread.stop()
