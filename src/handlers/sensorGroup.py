# -*- coding: utf-8 -*-

from enums.sensorDrivers import SensorDrivers as SDrivers
from handlers.sensor import Sensor


class SensorGroup:
    def __init__(self, group_name: str) -> None:
        self.group_name = group_name
        self.sensors = {}

    def addSensor(self, sensor_id: str, sensor_params: dict, required_config_keys: list, sensor_driver: SDrivers) -> None:
        if not all(key in sensor_params.keys() for key in required_config_keys):
            return
        sensor = Sensor(sensor_id, sensor_params, sensor_driver)
        self.sensors[sensor_id] = sensor

    def checkConnections(self) -> bool:
        pass

    def start(self) -> None:
        pass

    def register(self) -> None:
        pass

    def stop(self) -> None:
        pass
