from loguru import logger
from src.managers.configManager import ConfigManager
from src.handlers import SensorGroup, Sensor
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorParams import SensorParams as SParams
from src.enums.sensorDrivers import SensorDrivers as SDrivers


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
            SDrivers.PHIDGET_LOADCELL_DRIVER,
        )
        self.sensor_group_platform2 = self.setSensorGroup(
            "Platform 2",
            CfgPaths.PHIDGET_P2_LOADCELL_CONFIG_SECTION,
            self.required_keys_loadcells,
            SDrivers.PHIDGET_LOADCELL_DRIVER,
        )
        self.sensor_group_encoders = self.setSensorGroup(
            "Barbell encoders",
            CfgPaths.PHIDGET_ENCODER_CONFIG_SECTION,
            self.required_keys_encoders,
            SDrivers.PHIDGET_ENCODER_DRIVER,
        )
        self.sensor_group_imus = self.setSensorGroup(
            "Body IMUs",
            CfgPaths.TAOBOTICS_IMU_CONFIG_SECTION,
            self.required_keys_taobotics,
            SDrivers.TAOBOTICS_IMU_DRIVER,
        )
        self.ref_sensor = self.setSensor(
            "REF",
            CfgPaths.CALIBRATION_CONFIG_SECTION,
            self.required_keys_loadcells,
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

    def setSensor(
        self,
        name: str,
        config_section: CfgPaths,
        required_keys: list,
        sensor_driver: SDrivers,
    ) -> Sensor:
        ref_sensor_section = self.config_mngr.getConfigValue(config_section.value, None)
        if ref_sensor_section is None:
            return None
        if not all(key.value in ref_sensor_section.keys() for key in required_keys):
            return None
        return Sensor(name, ref_sensor_section, sensor_driver)

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
