# -*- coding: utf-8 -*-

import concurrent.futures

from src.enums.sensorDrivers import SensorDrivers as SDrivers
from src.handlers.sensor import Sensor


class SensorGroup:
    def __init__(self, group_name: str) -> None:
        self.group_name = group_name
        self.sensors = {}

    def addSensor(self, sensor_id: str, sensor_params: dict, required_config_keys: list, sensor_driver: SDrivers) -> None:
        if not all(key.value in sensor_params.keys() for key in required_config_keys):
            return
        sensor = Sensor(sensor_id, sensor_params, sensor_driver)
        self.sensors[sensor_id] = sensor

    def checkConnections(self) -> bool:
        results = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensors_list = list(self.sensors.values())
            results = list(executor.map(
                lambda sensor: sensor.connect(), sensors_list))
            executor.map(lambda sensor: sensor.disconnect(), sensors_list)
        return any(results)

    def start(self) -> None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensors_list = list(self.sensors.values())
            executor.map(lambda sensor: sensor.connect(), sensors_list)

    def register(self) -> None:
        [sensor.registerValue() for sensor in self.sensors.values()]

    def stop(self) -> None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensors_list = list(self.sensors.values())
            executor.map(lambda sensor: sensor.disconnect(), sensors_list)

    # Setters and getters

    def setSensorRead(self, sensor_id: str, read: bool) -> None:
        if sensor_id not in self.sensors.keys():
            return
        self.sensors[sensor_id].setRead(read)

    def getGroupName(self) -> str:
        return self.group_name
    
    def getGroupInfo(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            group_dict[sensor_id] = [
                sensor.getName(), sensor.getProperties(), sensor.getStatus(), sensor.getIsReadable()]
        return group_dict

    def getGroupSize(self) -> int:
        return len(self.sensors)

    def getGroupValues(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            group_dict[sensor_id] = sensor.getValues()
        return group_dict

    def getGroupCalibrationParams(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            group_dict[sensor_id] = sensor.getSlopeIntercept()
        return group_dict
