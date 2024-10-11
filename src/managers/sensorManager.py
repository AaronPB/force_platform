# -*- coding: utf-8 -*-

from loguru import logger
from src.handlers.sensorGroup import SensorGroup
from src.handlers.sensor import Sensor
from src.handlers import drivers
from src.enums.configPaths import ConfigPaths as CfgPaths
from src.enums.sensorParams import SParams, SGParams
from src.enums.sensorTypes import STypes, SGTypes
from src.enums.sensorStatus import SGStatus
from typing import Protocol

# Required param keys for sensor handlers
group_keys = [SGParams.NAME, SGParams.TYPE, SGParams.READ, SGParams.SENSOR_LIST]
sensor_keys = [SParams.NAME, SParams.TYPE, SParams.READ, SParams.CONNECTION_SECTION]
loadcell_conn_keys = [SParams.SERIAL, SParams.CHANNEL]
encoder_conn_keys = [SParams.SERIAL, SParams.CHANNEL]
taobotics_conn_keys = [SParams.SERIAL]


class ConfigYAMLHandler(Protocol):
    def setConfigValue(self, key_path: str, value) -> None: ...

    def getConfigValue(self, key_path: str, default_value=None): ...


class SensorManager:
    def __init__(self) -> None:
        self.config_mngr: ConfigYAMLHandler
        self.config_sensors: dict = {}

        self.sensor_groups: list[SensorGroup] = []

    def setup(self, config_manager: ConfigYAMLHandler) -> None:
        self.config_mngr = config_manager
        self.config_sensors = self.config_mngr.getConfigValue(
            CfgPaths.SENSORS_SECTION.value, {}
        )
        config_groups = self.config_mngr.getConfigValue(
            CfgPaths.SENSOR_GROUPS_SECTION.value, {}
        )
        self.clearSensors()
        self.loadSensorGroups(config_groups)

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
            # Add sensor group to list
            self.sensor_groups.append(sensor_group)
            logger.info(
                f"Sensor group {sensor_group.getID()} of type {sensor_group.getType().name} successfully loaded,"
                + f"with {sensor_group.getSize()} sensors."
            )

    def loadSensorGroup(self, id: str, content: dict) -> SensorGroup:
        if content is None:
            logger.warning(f"Sensor group {id} is empty! Not loaded.")
            return None
        if not all(key.value in content.keys() for key in group_keys):
            logger.warning(
                f"Sensor group {id} does not have the required keys! Not loaded."
            )
            return None
        if content[SGParams.TYPE.value] not in SGTypes._member_names_:
            logger.warning(
                f"Sensor group {id} does not have a valid group type! Not loaded."
            )
            return None
        if not content[SGParams.SENSOR_LIST.value]:
            logger.warning(f"Sensor group {id} has an empty sensor list! Not loaded.")
            return None
        sensor_group = SensorGroup(
            id, content[SGParams.NAME.value], SGTypes[content[SGParams.TYPE.value]]
        )
        sensor_group.setRead(content[SGParams.READ.value])
        # Load all sensors for this sensor group
        for sensor_id in content[SGParams.SENSOR_LIST.value]:
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
        # Sections are required: name, type, read and connection.
        # Optional sections: calibration and properties.
        if not all(key.value in content.keys() for key in sensor_keys):
            logger.warning(f"Sensor {id} does not have the required keys! Not loaded.")
            return None
        if content[SParams.TYPE.value] not in STypes._member_names_:
            logger.warning(
                f"Sensor {id} does not have a valid sensor type! Not loaded."
            )
            return None
        # Check sensor type required keys and setup
        sensor = Sensor()
        if content[SParams.TYPE.value] == STypes.SENSOR_LOADCELL.name:
            if not all(
                key.value in content[SParams.CONNECTION_SECTION.value].keys()
                for key in loadcell_conn_keys
            ):
                logger.warning(
                    f"Sensor {id} does not have the required loadcell connection keys! Not loaded."
                )
                return None
            sensor.setup(id, content, drivers.PhidgetLoadCell)
            return sensor
        if content[SParams.TYPE.value] == STypes.SENSOR_ENCODER.name:
            if not all(
                key.value in content[SParams.CONNECTION_SECTION.value].keys()
                for key in encoder_conn_keys
            ):
                logger.warning(
                    f"Sensor {id} does not have the required encoder connection keys! Not loaded."
                )
                return None
            sensor.setup(id, content, drivers.PhidgetEncoder)
            return sensor
        if content[SParams.TYPE.value] == STypes.SENSOR_IMU.name:
            if not all(
                key.value in content[SParams.CONNECTION_SECTION.value].keys()
                for key in taobotics_conn_keys
            ):
                logger.warning(
                    f"Sensor {id} does not have the required taobotics connection keys! Not loaded."
                )
                return None
            sensor.setup(id, content, drivers.TaoboticsIMU)
            return sensor
        logger.error(
            f"Sensor type {content[SParams.TYPE.value]} is not a sensor type! Not loaded."
        )
        return None

    def clearSensors(self) -> None:
        self.sensor_groups.clear()

    # Setters and getters

    def setSensorRead(
        self,
        read: bool,
        group_id: str,
        sensor_id: str = None,
    ) -> None:
        for group in self.getGroups():
            if group.getID() != group_id:
                continue
            if sensor_id is None:
                logger.debug(f"Set read status of group {group_id} to {read}")
                group.setRead(read)
                self.config_mngr.setConfigValue(
                    CfgPaths.SENSOR_GROUPS_SECTION.value
                    + "."
                    + group_id
                    + "."
                    + SGParams.READ.value,
                    read,
                )
                return
            group_sensors = group.getSensors()
            if sensor_id in group_sensors:
                logger.debug(f"Set read status of sensor {sensor_id} to {read}")
                group_sensors[sensor_id].setRead(read)
                self.config_mngr.setConfigValue(
                    CfgPaths.SENSORS_SECTION.value
                    + "."
                    + sensor_id
                    + "."
                    + SParams.READ.value,
                    read,
                )
                return

    def setSensorSlopeByID(self, group_id: str, sensor_id: str, slope: float) -> None:
        group = self.getGroup(group_id)
        if group is None:
            return
        if sensor_id in group.getSensors().keys():
            self.setSensorSlope(group.getSensors()[sensor_id], slope)

    def setSensorSlope(self, sensor: Sensor, slope: float) -> None:
        sensor.setSlope(slope)
        self.config_mngr.setConfigValue(
            CfgPaths.SENSORS_SECTION.value
            + "."
            + sensor.getID()
            + "."
            + SParams.CALIBRATION_SECTION.value
            + "."
            + SParams.SLOPE.value,
            slope,
        )

    def setSensorInterceptByID(
        self, group_id: str, sensor_id: str, intercept: float
    ) -> None:
        group = self.getGroup(group_id)
        if group is None:
            return
        if sensor_id in group.getSensors().keys():
            self.setSensorIntercept(group.getSensors()[sensor_id], intercept)

    def setSensorIntercept(self, sensor: Sensor, intercept: float) -> None:
        sensor.setIntercept(intercept)
        self.config_mngr.setConfigValue(
            CfgPaths.SENSORS_SECTION.value
            + "."
            + sensor.getID()
            + "."
            + SParams.CALIBRATION_SECTION.value
            + "."
            + SParams.INTERCEPT.value,
            intercept,
        )

    def getGroups(
        self, only_available: bool = False, group_type: SGTypes = None
    ) -> list[SensorGroup]:
        if not only_available and group_type is None:
            return self.sensor_groups
        group_list: list[SensorGroup] = []
        for group in self.sensor_groups:
            if only_available and group.getStatus() == SGStatus.ERROR:
                continue
            if group_type is not None and group.getType() != group_type:
                continue
            group_list.append(group)
        return group_list

    def getGroup(self, group_id: str) -> SensorGroup:
        for group in self.getGroups():
            if group.getID() == group_id:
                return group
        return None
