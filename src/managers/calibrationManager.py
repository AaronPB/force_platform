# -*- coding: utf-8 -*-

import time

from src.managers.configManager import ConfigManager
from src.handlers import SensorGroup
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorParams import SensorParams as SParams
from src.enums.sensorDrivers import SensorDrivers as SDrivers


class CalibrationManager:
    def __init__(self, config_mngr: ConfigManager) -> None:
        # Global values
        self.config_mngr = config_mngr
        self.sensors_connected = False
        self.calib_sensor = None
        self.reference_sensor = None

        # Required config keys
        required_keys_loadcells = [
            SParams.NAME,
            SParams.READ,
            SParams.SERIAL,
            SParams.CHANNEL,
            SParams.CALIBRATION_SECTION,
        ]

        # Sensor group handlers
        self.sensor_group_platform1 = self.setSensorGroup(
            "Platform 1",
            CfgPaths.PHIDGET_P1_LOADCELL_CONFIG_SECTION,
            required_keys_loadcells,
            SDrivers.PHIDGET_LOADCELL_DRIVER,
        )
        self.sensor_group_platform2 = self.setSensorGroup(
            "Platform 2",
            CfgPaths.PHIDGET_P2_LOADCELL_CONFIG_SECTION,
            required_keys_loadcells,
            SDrivers.PHIDGET_LOADCELL_DRIVER,
        )

    def setSensorGroup(
        self,
        group_name: str,
        config_section: CfgPaths,
        required_keys: list,
        sensor_driver: SDrivers,
    ) -> SensorGroup:
        sensor_group = SensorGroup(group_name)
        for sensor_id in self.config_mngr.getConfigValue(config_section.value):
            sensor_params = self.config_mngr.getConfigValue(
                config_section.value + "." + sensor_id
            )
            sensor_group.addSensor(
                sensor_id, sensor_params, required_keys, sensor_driver
            )
        return sensor_group

    def checkConnection(self) -> bool:
        connection_results_list = [
            handler.checkConnections()
            for handler in [self.sensor_group_platform1, self.sensor_group_platform2]
        ]
        self.sensors_connected = any(connection_results_list)
        return self.sensors_connected

    # Setters and getters

    def calibrateP1Sensor(self, index: int) -> list:
        sensor_list = list(self.sensor_group_platform1.sensors.values())
        self.calib_sensor = sensor_list[index]
        return [self.calib_sensor.getName(), self.calib_sensor.getProperties()]

    def calibrateP2Sensor(self, index: int) -> None:
        sensor_list = list(self.sensor_group_platform2.sensors.values())
        self.calib_sensor = sensor_list[index]
        return [self.calib_sensor.getName(), self.calib_sensor.getProperties()]

    def getP1SensorStatus(self) -> dict:
        return self.sensor_group_platform1.getGroupInfo()

    def getP2SensorStatus(self) -> dict:
        return self.sensor_group_platform2.getGroupInfo()

    # Calibration functions

    def getValues(self):
        pass

    def getRegressionResults(self, data: dict):
        pass
