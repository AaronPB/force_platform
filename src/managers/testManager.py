import time

from managers.configManager import ConfigManager
from handlers import SensorGroup
from enums.configPaths import ConfigPaths as CfgPaths
from enums.sensorParams import SensorParams as SParams
from enums.sensorDrivers import SensorDrivers as SDrivers
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

    def setSensorGroup(self, group_name: str, config_section: CfgPaths, required_keys, sensor_driver: SDrivers) -> SensorGroup:
        sensor_group = SensorGroup(group_name)
        for sensor_id in self.config_mngr.getConfigValue(config_section):
            sensor_params = self.config_mngr.getConfigValue(
                config_section + '.' + sensor_id)
            sensor_group.addSensor(
                sensor_id, sensor_params, required_keys, sensor_driver)
        return sensor_group

    # Sensor setters and getters

    def setP1SensorRead(self, index: int, read: bool) -> None:
        group_ids = self.sensor_group_platform1.getGroupInfo().keys()
        sensor_id = group_ids[index]
        self.sensor_group_platform1.setSensorRead(sensor_id, read)
        self.config_mngr.setConfigValue(
            CfgPaths.PHIDGET_P1_LOADCELL_CONFIG_SECTION + '.' + str(sensor_id) + '.' + SParams.READ, read)

    def getP1SensorStatus(self) -> dict:
        return self.sensor_group_platform1.getGroupInfo()

    # TODO repeat this setters and getters other 3 times... maybe abstract methods?

    # Test methods
    def checkConnection(self) -> bool:
        self.sensors_connected = any(
            handler.checkConnections() for handler in self.sensor_group_list)
        return self.sensors_connected

    def testStart(self) -> None:
        [handler.start() for handler in self.sensor_group_list]

    def testRegisterValues(self) -> None:
        # TODO
        pass

    def testStop(self) -> None:
        [handler.stop() for handler in self.sensor_group_list]
