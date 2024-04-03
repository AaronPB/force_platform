# -*- coding: utf-8 -*-

import time
from loguru import logger
from src.handlers.sensorGroup import SensorGroup


class TestManager:
    __test__ = False

    def __init__(self) -> None:
        self.sensor_groups: list[SensorGroup]
        self.sensors_connected: bool = False
        self.test_times: list = []

    # Setters and getters
    def setSensorGroups(self, sensor_groups: list[SensorGroup]) -> None:
        self.sensor_groups = sensor_groups

    def getSensorConnected(self) -> bool:
        return self.sensors_connected

    def getTestTimes(self) -> list:
        return self.test_times

    # Test methods
    def checkConnection(self) -> bool:
        connection_results_list = [
            handler.checkConnections() for handler in self.sensor_groups
        ]
        self.sensors_connected = any(connection_results_list)
        return self.sensors_connected

    def testStart(self, test_name: str) -> None:
        logger.info(f"Starting test: {test_name}")
        self.test_times = []
        [handler.clearValues() for handler in self.sensor_groups]
        [handler.start() for handler in self.sensor_groups]

    def testRegisterValues(self) -> None:
        self.test_times.append(round(time.time() * 1000))
        [handler.register() for handler in self.sensor_groups]

    def testStop(self, test_name: str) -> None:
        logger.info(f"Finish test: {test_name}")
        [handler.stop() for handler in self.sensor_groups]
