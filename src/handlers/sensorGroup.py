# -*- coding: utf-8 -*-

import concurrent.futures

from src.enums.sensorStatus import SensorStatus as SStatus
from src.handlers.sensor import Sensor


class SensorGroup:
    def __init__(self, group_name: str) -> None:
        self.group_name = group_name
        self.is_group_active = False
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
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensors_list = list(self.sensors.values())
            executor.map(lambda sensor: sensor.disconnect(), sensors_list)
        self.is_group_active = False

    # Setters and getters

    def setSensorRead(self, sensor_id: str, read: bool) -> None:
        if sensor_id not in self.sensors.keys():
            return
        self.sensors[sensor_id].setRead(read)

    def tareSensors(self, mean_dict: dict) -> None:
        for sensor_id, mean in mean_dict.items():
            sensor = self.sensors.get(sensor_id)
            current_params = sensor.getSlopeIntercept()
            sensor.setIntercept(float(current_params[1] - mean))

    def clearSensorValues(self) -> None:
        [sensor.clearValues() for sensor in self.sensors.values()]

    def getGroupName(self) -> str:
        return self.group_name

    def getGroupInfo(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            group_dict[sensor_id] = [
                sensor.getName(),
                sensor.getProperties(),
                sensor.getStatus(),
                sensor.getIsReadable(),
            ]
        return group_dict

    def getGroupAvailableInfo(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            if sensor.getStatus() is not SStatus.AVAILABLE:
                continue
            group_dict[sensor_id] = [
                sensor.getName(),
                sensor.getProperties(),
                sensor.getStatus(),
                sensor.getIsReadable(),
            ]
        return group_dict

    def getGroupSize(self) -> int:
        return len(self.sensors)

    def getGroupIsActive(self) -> bool:
        return self.is_group_active

    def getGroupValues(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            if sensor.getStatus() is not SStatus.AVAILABLE:
                continue
            group_dict[sensor_id] = sensor.getValues()
        return group_dict

    def getGroupCalibValues(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            if sensor.getStatus() is not SStatus.AVAILABLE:
                continue
            group_dict[sensor_id] = sensor.getCalibValues()
        return group_dict

    def getGroupCalibrationParams(self) -> dict:
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            group_dict[sensor_id] = sensor.getSlopeIntercept()
        return group_dict
