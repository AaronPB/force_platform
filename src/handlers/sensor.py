# -*- coding: utf-8 -*-

from src.enums.sensorParams import SensorParams as SParams
from src.enums.sensorStatus import SensorStatus as SStatus
from src.enums.sensorDrivers import SensorDrivers as SDrivers


class Sensor:
    def __init__(self, sensor_id: str, sensor_params: dict, sensor_driver: SDrivers) -> None:
        self.id = sensor_id
        self.params = sensor_params
        self.status = SStatus.IGNORED
        self.driver = sensor_driver.value(
            self.params[SParams.SERIAL.value], self.params.get(SParams.CHANNEL.value, None))
        self.values = []

    def connect(self) -> bool:
        if not self.params[SParams.READ.value]:
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

    # Setters and getters methods

    def setRead(self, read: bool) -> None:
        self.params[SParams.READ.value] = read

    def getName(self) -> str:
        return self.params[SParams.NAME.value]

    def getStatus(self) -> SStatus:
        return self.status

    def getIsReadable(self) -> bool:
        return self.params[SParams.READ.value]

    def getProperties(self) -> str:
        text = ' - '
        for property in self.params[SParams.PROPERTIES_SECTION.value]:
            text = text + \
                self.params[SParams.PROPERTIES_SECTION.value][property] + ' - '
        return text

    def getSlopeIntercept(self) -> list:
        slope = self.params[SParams.CALIBRATION_SECTION.value][SParams.SLOPE.value]
        intercept = self.params[SParams.CALIBRATION_SECTION.value][SParams.INTERCEPT.value]
        if slope is None:
            slope = 1
        if intercept is None:
            intercept = 0
        return [slope, intercept]

    def getValues(self) -> list:
        return self.values
