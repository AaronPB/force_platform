# -*- coding: utf-8 -*-

from loguru import logger
from src.managers.configManager import ConfigManager
from src.handlers.sensorGroup import SensorGroup
from src.handlers.sensor import Sensor, Driver
from src.handlers.drivers import PhidgetLoadCell, PhidgetEncoder, TaoboticsIMU
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorParams import SParams, SGParams
from src.enums.sensorTypes import STypes, SGTypes

# Required param keys for sensor handlers
group_keys = [
    SGParams.NAME,
    SGParams.TYPE,
    SGParams.READ,
    SGParams.SENSOR_LIST,
]
sensor_keys = [SParams.NAME, SParams.TYPE, SParams.READ, SParams.CONNECTION_SECTION]
loadcell_keys = [SParams.SERIAL, SParams.CHANNEL]
encoder_keys = [
    SParams.SERIAL,
    SParams.CHANNEL,
    SParams.INITIAL_POS,
]
taobotics_keys = [SParams.NAME, SParams.SERIAL]


class SensorLoader:
    def __init__(self) -> None:
        self.config_sensors: dict = {}

        self.sensor_groups: list[SensorGroup] = []
        self.platform_groups: list[SensorGroup] = []
        self.encoder_groups: list[SensorGroup] = []
        self.imu_groups: list[SensorGroup] = []

        self.loadcell_calib_ref: Sensor = None
        self.platform_calib_ref: Sensor = None

    def setup(self, config_mngr: ConfigManager) -> None:
        self.config_sensors = config_mngr.getConfigValue(
            CfgPaths.SENSORS_SECTION.value, {}
        )
        config_groups = config_mngr.getConfigValue(
            CfgPaths.SENSOR_GROUPS_SECTION.value, {}
        )
        loadcell_calib_id = config_mngr.getConfigValue(
            CfgPaths.CALIBRATION_LOADCELL_SENSOR.value, {}
        )
        platform_calib_id = config_mngr.getConfigValue(
            CfgPaths.CALIBRATION_PLATFORM_SENSOR.value, {}
        )
        self.loadSensorGroups(config_groups)
        self.loadcell_calib_ref = self.loadSensor(loadcell_calib_id)
        self.platform_calib_ref = self.loadSensor(platform_calib_id)

    def loadSensorGroups(self, config_groups: dict) -> None:
        if not config_groups:
            logger.error("No sensor groups found in config!")
            return
        if not self.config_sensors:
            logger.error("No sensors found in config!")
            return
        for group_id in config_groups:
            sensor_group = self.loadSensorGroup(group_id, config_groups[group_id])
            if sensor_group is None:
                continue
            # TODO check group type (for certain groups such as platforms)
            # TODO add group to list

    def loadSensorGroup(self, id: str, content: dict) -> SensorGroup:
        if content is None:
            logger.warning(f"Sensor group {id} is empty! Not loaded.")
            return None
        if not all(key.value in content.keys() for key in group_keys):
            logger.warning(
                f"Sensor group {id} does not have the required keys! Not loaded."
            )
            return None
        if not content[SGParams.SENSOR_LIST.value]:
            logger.warning(f"Sensor group {id} has an empty sensor list! Not loaded.")
            return None
        sensor_group = SensorGroup(id, content[SGParams.NAME.value])
        # Load all sensors for this sensor group
        for sensor_id in content[SGParams.SENSOR_LIST]:
            sensor = self.loadSensor(sensor_id)
            if sensor is not None:
                sensor_group.addSensor(sensor)
        # Check if any sensor has been loaded
        if sensor_group.getSize() == 0:
            logger.error(f"Sensor group {id} is empty. Not loaded.")
            return None
        return sensor_group

    def loadSensor(self, id: str) -> Sensor:
        if not id in self.config_sensors:
            logger.warning(
                f"Did not found sensor {id} in sensors config section. Not loaded."
            )
            return None
        content = self.config_sensors[id]
        # TODO Now sensor params needs to have a generic style.
        # Following sections are required: name, type and connection.
        # Optional sections: calibration and properties.
        if not all(key.value in content.keys() for key in sensor_keys):
            logger.warning(f"Sensor {id} does not have the required keys! Not loaded.")
            return None
        if content[SParams.TYPE.value] not in STypes:
            logger.warning(
                f"Sensor {id} does not have a valid sensor type! Not loaded."
            )
            return None
        # TODO sensor params
        sensor = Sensor()
        sensor.setup(id, {}, STypes[content[SParams.TYPE.value]].value)
        return sensor

    def getGroups(self) -> list:
        return self.sensor_groups

    def getPlatformGroups(self) -> SensorGroup:
        return self.platform_groups

    def getEncoderGroups(self) -> SensorGroup:
        return self.encoder_groups

    def getIMUGroups(self) -> SensorGroup:
        return self.imu_groups

    def getSensorCalibRef(self) -> Sensor:
        pass

    def getPlatformCalibRef(self) -> Sensor:
        pass
