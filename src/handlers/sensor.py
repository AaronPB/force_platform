# -*- coding: utf-8 -*-

from src.enums.sensorParams import SensorParams as SParams
from src.enums.sensorStatus import SensorStatus as SStatus
from src.enums.sensorDrivers import SensorDrivers as SDrivers


class Sensor:
    def __init__(
        self, sensor_id: str, sensor_params: dict, sensor_driver: SDrivers
    ) -> None:
        self.id = sensor_id
        self.params = sensor_params
        self.status = SStatus.IGNORED
        self.driver = sensor_driver.value(
            self.params[SParams.SERIAL.value],
            self.params.get(SParams.CHANNEL.value, None),
        )
        self.values = []

    def connect(self, check: bool = False) -> bool:
        if not self.params[SParams.READ.value]:
            self.status = SStatus.IGNORED
            return False
        if not check and self.status is not SStatus.AVAILABLE:
            return False
        self.status = SStatus.NOT_FOUND
        if self.driver.connect():
            self.status = SStatus.AVAILABLE
            return True
        return False

    def disconnect(self) -> None:
        self.driver.disconnect()

    def checkConnection(self) -> bool:
        connected = self.connect(check=True)
        if connected:
            self.disconnect()
        return connected

    def registerValue(self) -> None:
        if self.status is not SStatus.AVAILABLE:
            return
        self.values.append(self.driver.getValue())

    # Setters and getters methods

    def setRead(self, read: bool) -> None:
        self.params[SParams.READ.value] = read

    def setIntercept(self, intercept: float) -> None:
        self.params[SParams.CALIBRATION_SECTION.value][
            SParams.INTERCEPT.value
        ] = intercept

    def clearValues(self) -> None:
        self.values.clear()

    def getName(self) -> str:
        return self.params[SParams.NAME.value]

    def getStatus(self) -> SStatus:
        return self.status

    def getIsReadable(self) -> bool:
        return self.params[SParams.READ.value]

    def getProperties(self) -> str:
        text = " - "
        for property in self.params[SParams.PROPERTIES_SECTION.value]:
            text = (
                text + self.params[SParams.PROPERTIES_SECTION.value][property] + " - "
            )
        return text

    def getSlopeIntercept(self) -> list:
        calib_params = self.params[SParams.CALIBRATION_SECTION.value]
        slope = calib_params.get(SParams.SLOPE.value, 1)
        intercept = calib_params.get(SParams.INTERCEPT.value, 0)
        return [slope, intercept]

    def getValues(self) -> list:
        return self.values

    def getCalibValues(self) -> list:
        calib_params = self.getSlopeIntercept()
        return [calib_params[0] * value + calib_params[1] for value in self.values]
