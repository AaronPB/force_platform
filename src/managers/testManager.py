# -*- coding: utf-8 -*-

import time
from loguru import logger
from src.managers.configManager import ConfigManager
from src.managers.sensorManager import SensorManager
from src.handlers import SensorGroup
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorParams import SensorParams as SParams


class TestManager:
    __test__ = False

    def __init__(
        self, config_mngr: ConfigManager, sensor_manager: SensorManager
    ) -> None:
        # Global values
        self.config_mngr = config_mngr
        self.sensor_mngr = sensor_manager
        self.sensors_connected = False
        self.test_times = []

    # Sensor setters and getters

    def getP1SensorStatus(self) -> dict:
        return self.group_platform1.getGroupInfo()

    def getP2SensorStatus(self) -> dict:
        return self.group_platform2.getGroupInfo()

    def getOthersSensorStatus(self) -> dict:
        encoder_dict = self.group_encoders.getGroupInfo()
        imu_dict = self.group_imus.getGroupInfo()
        return {**encoder_dict, **imu_dict}

    def getSensorConnected(self) -> bool:
        return self.sensors_connected

    def getTestTimes(self) -> list:
        return self.test_times

    # Test methods
    def checkConnection(self) -> bool:
        connection_results_list = [
            handler.checkConnections() for handler in self.sensor_mngr.getGroups()
        ]
        self.sensors_connected = any(connection_results_list)
        return self.sensors_connected

    def testStart(self, test_name: str) -> None:
        logger.info(f"Starting test: {test_name}")
        self.test_times = []
        [handler.clearSensorValues() for handler in self.sensor_mngr.getGroups()]
        [handler.start() for handler in self.sensor_mngr.getGroups()]

    def testRegisterValues(self) -> None:
        self.test_times.append(round(time.time() * 1000))
        [handler.register() for handler in self.sensor_mngr.getGroups()]

    def testStop(self, test_name: str) -> None:
        logger.info(f"Finish test: {test_name}")
        [handler.stop() for handler in self.sensor_mngr.getGroups()]
        # Save modified intercepts in config
        self.config_mngr.saveConfig()
