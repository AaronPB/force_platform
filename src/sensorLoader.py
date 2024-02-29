# -*- coding: utf-8 -*-

from loguru import logger
from src.managers.configManager import ConfigManager
from src.handlers.sensorGroup import SensorGroup
from src.handlers.sensor import Sensor, Driver
from src.handlers.drivers import PhidgetLoadCell, PhidgetEncoder, TaoboticsIMU
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorParams import SensorParams as SParams


class SensorLoader:
    def __init__(self, config_mngr: ConfigManager) -> None:
        # Global values
        self.config_mngr = config_mngr

        # Required config keys for each sensor group
        self.required_keys_loadcells = [
            SParams.NAME,
            SParams.READ,
            SParams.SERIAL,
            SParams.CHANNEL,
            SParams.CALIBRATION_SECTION,
        ]
        self.required_keys_encoders = [
            SParams.NAME,
            SParams.READ,
            SParams.SERIAL,
            SParams.CHANNEL,
            SParams.CALIBRATION_SECTION,
            SParams.INITIAL_POS,
        ]
        self.required_keys_taobotics = [SParams.NAME, SParams.READ, SParams.SERIAL]

    def loadHandlers(self):
        self.sensor_group_platform1 = self.setSensorGroup(
            "Platform 1",
            CfgPaths.PHIDGET_P1_LOADCELL_CONFIG_SECTION,
            self.required_keys_loadcells,
            PhidgetLoadCell,
        )
        self.sensor_group_platform2 = self.setSensorGroup(
            "Platform 2",
            CfgPaths.PHIDGET_P2_LOADCELL_CONFIG_SECTION,
            self.required_keys_loadcells,
            PhidgetLoadCell,
        )
        self.sensor_group_encoders = self.setSensorGroup(
            "Barbell encoders",
            CfgPaths.PHIDGET_ENCODER_CONFIG_SECTION,
            self.required_keys_encoders,
            PhidgetEncoder,
        )
        self.sensor_group_imus = self.setSensorGroup(
            "Body IMUs",
            CfgPaths.TAOBOTICS_IMU_CONFIG_SECTION,
            self.required_keys_taobotics,
            TaoboticsIMU,
        )
        self.ref_sensor = Sensor()
        self.loadSensor(
            self.ref_sensor,
            "REF",
            CfgPaths.CALIBRATION_CONFIG_SECTION.value,
            self.required_keys_loadcells,
            PhidgetLoadCell,
        )

    def setSensorGroup(
        self,
        group_name: str,
        config_section: CfgPaths,
        required_keys: list,
        sensor_driver: Driver,
    ) -> SensorGroup:
        sensor_group = SensorGroup(group_name)
        for sensor_id in self.config_mngr.getConfigValue(config_section.value):
            sensor = Sensor()
            config_path = config_section.value + "." + sensor_id
            setup = self.loadSensor(
                sensor, sensor_id, config_path, required_keys, sensor_driver
            )
            if not setup:
                logger.warning(f"Could not load sensor in config path {config_path}!")
                continue
            sensor_group.addSensor(sensor)
        return sensor_group

    def loadSensor(
        self,
        sensor: Sensor,
        id: str,
        config_path: str,
        required_keys: list,
        driver: Driver,
    ) -> bool:
        sensor_params = self.config_mngr.getConfigValue(config_path, None)
        if sensor_params is None:
            return False
        if not all(key.value in sensor_params.keys() for key in required_keys):
            return False
        sensor.setup(id, sensor_params, driver)
        return True

    def getSensorGroups(self) -> list:
        return [
            self.sensor_group_platform1,
            self.sensor_group_platform2,
            self.sensor_group_encoders,
            self.sensor_group_imus,
        ]

    def getSensorGroupPlatform1(self) -> SensorGroup:
        return self.sensor_group_platform1

    def getSensorGroupPlatform2(self) -> SensorGroup:
        return self.sensor_group_platform2

    def getSensorGroupEncoders(self) -> SensorGroup:
        return self.sensor_group_encoders

    def getSensorGroupIMUs(self) -> SensorGroup:
        return self.sensor_group_imus

    def getRefSensor(self) -> Sensor:
        return self.ref_sensor
