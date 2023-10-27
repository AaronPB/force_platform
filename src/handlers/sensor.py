# -*- coding: utf-8 -*-

from enums.sensorParams import SensorParams as SParams
from enums.sensorStatus import SensorStatus as SStatus
from enums.sensorDrivers import SensorDrivers as SDrivers


class Sensor:
    def __init__(self, sensor_id: str, sensor_params: dict, sensor_driver: SDrivers) -> None:
        self.id = sensor_id
        self.params = sensor_params
        self.status = SStatus.IGNORED
        self.driver = sensor_driver.value(
            self.params[SParams.SERIAL], self.params[SParams.CHANNEL])
        self.values = []

    def connect(self) -> bool:
        if not self.params[SParams.READ]:
            return False
        self.status = SStatus.NOT_FOUND
        if self.driver.connect():
            self.status = SStatus.AVAILABLE
            return True
        return False

    def disconnect(self) -> None:
        self.driver.disconnect()

    def checkConnection(self) -> bool:
        connected = self.connect()
        if connected:
            self.disconnect()
        return connected

    def registerValue(self) -> None:
        self.values.append(self.driver.getValue())

    # Getter methods

    def getName(self) -> str:
        return self.params[SParams.NAME]

    def getStatus(self) -> SStatus:
        return self.status

    def getProperties(self) -> str:
        text = ''
        for property in self.params[SParams.PROPERTIES_SECTION]:
            text = text + '|' + \
                self.params[SParams.PROPERTIES_SECTION][property]
        return text

    def getSlopeIntercept(self) -> list:
        slope = self.params[SParams.CALIBRATION_SECTION][SParams.SLOPE]
        intercept = self.params[SParams.CALIBRATION_SECTION][SParams.INTERCEPT]
        if slope is None:
            slope = 1
        if intercept is None:
            intercept = 0
        return [slope, intercept]

    def getValues(self) -> list:
        return self.values
