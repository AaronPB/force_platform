# -*- coding: utf-8 -*-

import concurrent.futures

from src.enums.sensorStatus import SensorStatus as SStatus
from src.handlers.sensor import Sensor


class SensorGroup:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
        self.active = False
        self.sensors: dict[str, Sensor] = {}

    def addSensor(self, sensor: Sensor):
        self.sensors[sensor.id] = sensor

    def checkConnections(self) -> bool:
        results = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensors_list = list(self.sensors.values())
            results = list(
                executor.map(lambda sensor: sensor.checkConnection(), sensors_list)
            )
        return any(results)

    def start(self) -> None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensors_list = list(self.sensors.values())
            results = list(executor.map(lambda sensor: sensor.connect(), sensors_list))
            self.is_group_active = any(results)

    def register(self) -> None:
        [sensor.registerValue() for sensor in self.sensors.values()]

    def stop(self) -> None:
        [sensor.disconnect() for sensor in list(self.sensors.values())]
        self.is_group_active = False

    # Setters and getters

    def setActive(self, active: bool) -> None:
        self.active = active

    def tareSensors(self, mean_dict: dict) -> None:
        for sensor_id, mean in mean_dict.items():
            sensor = self.sensors.get(sensor_id)
            sensor.setIntercept(float(sensor.getIntercept() - mean))

    def clearValues(self) -> None:
        [sensor.clearValues() for sensor in self.sensors.values()]

    def getID(self) -> str:
        return self.id

    def getName(self) -> str:
        return self.name

    def getSize(self) -> int:
        return len(self.sensors)

    def isActive(self) -> bool:
        return self.active

    def getValues(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            if sensor.getStatus() is not SStatus.AVAILABLE:
                continue
            group_dict[sensor_id] = sensor.getValues()
        return group_dict

    def getSlopes(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            if sensor.getStatus() is not SStatus.AVAILABLE:
                continue
            group_dict[sensor_id] = sensor.getSlope()
        return group_dict

    def getIntercepts(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            if sensor.getStatus() is not SStatus.AVAILABLE:
                continue
            group_dict[sensor_id] = sensor.getIntercept()
        return group_dict
