# -*- coding: utf-8 -*-

import concurrent.futures

from src.enums.sensorStatus import SStatus, SGStatus
from src.enums.sensorTypes import SGTypes, STypes
from src.handlers.sensor import Sensor


class SensorGroup:
    def __init__(self, id: str, name: str, type: SGTypes) -> None:
        self.id: str = id
        self.name: str = name
        self.type: SGTypes = type
        self.read: bool = False
        self.status: SGStatus = SGStatus.IGNORED
        self.active: bool = False
        self.sensors: dict[str, Sensor] = {}

    def addSensor(self, sensor: Sensor):
        self.sensors[sensor.id] = sensor

    def checkConnections(self) -> bool:
        if not self.read:
            self.status = SGStatus.IGNORED
            return False
        results = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensors_list = list(self.sensors.values())
            results = list(
                executor.map(lambda sensor: sensor.checkConnection(), sensors_list)
            )
        self.status = SGStatus.ERROR
        if all(results):
            self.status = SGStatus.OK
        elif any(results):
            self.status = SGStatus.WARNING
        return self.status != SGStatus.ERROR

    def start(self) -> None:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            sensors_list = list(self.sensors.values())
            results = list(executor.map(lambda sensor: sensor.connect(), sensors_list))
            self.active = any(results)

    def register(self) -> None:
        [sensor.registerValue() for sensor in self.sensors.values()]

    def stop(self) -> None:
        [sensor.disconnect() for sensor in list(self.sensors.values())]
        self.active = False

    # Setters and getters

    def setRead(self, read: bool) -> None:
        self.read = read

    def clearValues(self) -> None:
        [sensor.clearValues() for sensor in self.sensors.values()]

    def getID(self) -> str:
        return self.id

    def getName(self) -> str:
        return self.name

    def getType(self) -> SGTypes:
        return self.type

    def getSize(self) -> int:
        return len(self.sensors)

    def getRead(self) -> bool:
        return self.read

    def getStatus(self) -> SGStatus:
        return self.status

    def isActive(self) -> bool:
        return self.active

    def getSensors(
        self, only_available: bool = False, sensor_type: STypes = None
    ) -> dict[str, Sensor]:
        if not only_available and sensor_type is None:
            return self.sensors
        group_dict = {}
        for sensor_id, sensor in self.sensors.items():
            if only_available and sensor.getStatus() != SStatus.AVAILABLE:
                continue
            if sensor_type is not None and sensor.getType() != sensor_type:
                continue
            group_dict[sensor_id] = sensor
        return group_dict
