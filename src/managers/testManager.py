# -*- coding: utf-8 -*-

from src.managers.configManager import ConfigManager
from src.handlers import SensorGroup
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorParams import SensorParams as SParams
from src.enums.sensorDrivers import SensorDrivers as SDrivers
from src.utils import LogHandler


class TestManager:
    def __init__(self, config_mngr: ConfigManager) -> None:
        self.log_handler = LogHandler(str(__class__.__name__))

        # Global values
        self.config_mngr = config_mngr
        self.sensors_connected = False

        # Required config keys for each sensor group
        required_keys_loadcells = [SParams.NAME, SParams.READ, SParams.SERIAL,
                                   SParams.CHANNEL, SParams.CALIBRATION_SECTION]
        required_keys_encoders = [SParams.NAME, SParams.READ, SParams.SERIAL,
                                  SParams.CHANNEL, SParams.CALIBRATION_SECTION, SParams.INITIAL_POS]
        required_keys_taobotics = [SParams.NAME, SParams.READ, SParams.SERIAL]

        # Sensor group handlers
        self.sensor_group_platform1 = self.setSensorGroup(
            'Platform 1', CfgPaths.PHIDGET_P1_LOADCELL_CONFIG_SECTION,
            required_keys_loadcells, SDrivers.PHIDGET_LOADCELL_DRIVER)
        self.sensor_group_platform2 = self.setSensorGroup(
            'Platform 2', CfgPaths.PHIDGET_P2_LOADCELL_CONFIG_SECTION,
            required_keys_loadcells, SDrivers.PHIDGET_LOADCELL_DRIVER)
        self.sensor_group_encoders = self.setSensorGroup(
            'Barbell encoders', CfgPaths.PHIDGET_ENCODER_CONFIG_SECTION,
            required_keys_encoders, SDrivers.PHIDGET_ENCODER_DRIVER)
        self.sensor_group_imus = self.setSensorGroup(
            'Body IMUs', CfgPaths.TAOBOTICS_IMU_CONFIG_SECTION,
            required_keys_taobotics, SDrivers.TAOBOTICS_IMU_DRIVER)
        self.sensor_group_list = [self.sensor_group_platform1, self.sensor_group_platform2,
                                  self.sensor_group_encoders, self.sensor_group_imus]

    def setSensorGroup(self, group_name: str, config_section: CfgPaths, required_keys: list, sensor_driver: SDrivers) -> SensorGroup:
        sensor_group = SensorGroup(group_name)
        for sensor_id in self.config_mngr.getConfigValue(config_section.value):
            sensor_params = self.config_mngr.getConfigValue(
                config_section.value + '.' + sensor_id)
            sensor_group.addSensor(
                sensor_id, sensor_params, required_keys, sensor_driver)
        return sensor_group

    # Sensor setters and getters

    def setSensorRead(self, sensor_group: SensorGroup, config_section: CfgPaths, index: int, read: bool) -> None:
        group_ids = list(sensor_group.getGroupInfo().keys())
        sensor_id = group_ids[index]
        sensor_group.setSensorRead(sensor_id, read)
        self.config_mngr.setConfigValue(
            config_section.value + '.' + sensor_id + '.' + SParams.READ.value, read)

    def setP1SensorRead(self, index: int, read: bool) -> None:
        self.setSensorRead(self.sensor_group_platform1,
                           CfgPaths.PHIDGET_P1_LOADCELL_CONFIG_SECTION, index, read)

    def setP2SensorRead(self, index: int, read: bool) -> None:
        self.setSensorRead(self.sensor_group_platform2,
                           CfgPaths.PHIDGET_P2_LOADCELL_CONFIG_SECTION, index, read)

    def setOthersSensorRead(self, index: int, read: bool) -> None:
        ptr = self.sensor_group_encoders.getGroupSize()
        if index < ptr:
            self.setSensorRead(self.sensor_group_encoders,
                               CfgPaths.PHIDGET_ENCODER_CONFIG_SECTION, index, read)
            return
        self.setSensorRead(self.sensor_group_imus,
                           CfgPaths.TAOBOTICS_IMU_CONFIG_SECTION, index-ptr, read)

    def getP1SensorStatus(self) -> dict:
        return self.sensor_group_platform1.getGroupInfo()

    def getP2SensorStatus(self) -> dict:
        return self.sensor_group_platform2.getGroupInfo()

    def getOthersSensorStatus(self) -> dict:
        encoder_dict = self.sensor_group_encoders.getGroupInfo()
        imu_dict = self.sensor_group_imus.getGroupInfo()
        return {**encoder_dict, **imu_dict}

    def getSensorConnected(self) -> bool:
        return self.sensors_connected

    # Test methods
    def checkConnection(self) -> bool:
        connection_results_list = [
            handler.checkConnections() for handler in self.sensor_group_list]
        self.sensors_connected = any(connection_results_list)
        return self.sensors_connected

    def testStart(self) -> None:
        [handler.start() for handler in self.sensor_group_list]

    def testRegisterValues(self) -> None:
        [handler.register() for handler in self.sensor_group_list]

    def testStop(self) -> None:
        [handler.stop() for handler in self.sensor_group_list]
