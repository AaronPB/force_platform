# -*- coding: utf-8 -*-

import time
from loguru import logger
from src.managers.configManager import ConfigManager
from src.sensorLoader import SensorLoader
from src.handlers import SensorGroup
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorParams import SensorParams as SParams


class TestManager:
    def __init__(self, config_mngr: ConfigManager, sensor_loader: SensorLoader) -> None:
        # Global values
        self.config_mngr = config_mngr
        self.sensor_loader = sensor_loader
        self.group_platform1 = sensor_loader.getSensorGroupPlatform1()
        self.group_platform2 = sensor_loader.getSensorGroupPlatform2()
        self.group_encoders = sensor_loader.getSensorGroupEncoders()
        self.group_imus = sensor_loader.getSensorGroupIMUs()
        self.sensors_connected = False
        self.test_times = []

    # Sensor setters and getters

    def setSensorRead(
        self,
        sensor_group: SensorGroup,
        config_section: CfgPaths,
        index: int,
        read: bool,
    ) -> None:
        group_ids = list(sensor_group.getGroupInfo().keys())
        sensor_id = group_ids[index]
        sensor_group.setSensorRead(sensor_id, read)
        self.config_mngr.setConfigValue(
            config_section.value + "." + sensor_id + "." + SParams.READ.value, read
        )

    def setP1SensorRead(self, index: int, read: bool) -> None:
        self.setSensorRead(
            self.group_platform1,
            CfgPaths.PHIDGET_P1_LOADCELL_CONFIG_SECTION,
            index,
            read,
        )

    def setP2SensorRead(self, index: int, read: bool) -> None:
        self.setSensorRead(
            self.group_platform2,
            CfgPaths.PHIDGET_P2_LOADCELL_CONFIG_SECTION,
            index,
            read,
        )

    def setOthersSensorRead(self, index: int, read: bool) -> None:
        ptr = self.group_encoders.getGroupSize()
        if index < ptr:
            self.setSensorRead(
                self.group_encoders,
                CfgPaths.PHIDGET_ENCODER_CONFIG_SECTION,
                index,
                read,
            )
            return
        self.setSensorRead(
            self.group_imus,
            CfgPaths.TAOBOTICS_IMU_CONFIG_SECTION,
            index - ptr,
            read,
        )

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
            handler.checkConnections()
            for handler in self.sensor_loader.getSensorGroups()
        ]
        self.sensors_connected = any(connection_results_list)
        return self.sensors_connected

    def testStart(self, test_name: str) -> None:
        logger.info(f"Starting test: {test_name}")
        self.test_times = []
        [
            handler.clearSensorValues()
            for handler in self.sensor_loader.getSensorGroups()
        ]
        [handler.start() for handler in self.sensor_loader.getSensorGroups()]

    def testRegisterValues(self) -> None:
        self.test_times.append(round(time.time() * 1000))
        [handler.register() for handler in self.sensor_loader.getSensorGroups()]

    def testStop(self, test_name: str) -> None:
        logger.info(f"Finish test: {test_name}")
        [handler.stop() for handler in self.sensor_loader.getSensorGroups()]
        # Save modified intercepts in config
        self.config_mngr.saveConfig()
