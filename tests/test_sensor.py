# -*- coding: utf-8 -*-

from src.handlers.sensor import Sensor, Driver
from src.enums.sensorStatus import SensorStatus as SStatus
from src.enums.sensorParams import SensorParams as SParams
import pytest


# General mocks, builders and fixtures


class AvailableDriverMock:
    def __init__(self, serial: int, channel: int) -> None:
        pass

    def connect(self, check: bool = False):
        return True

    def disconnect(self):
        pass

    def getValue(self):
        return 10


class UnavailableDriverMock:
    def __init__(self, serial: int, channel: int) -> None:
        pass

    def connect(self, check: bool = False):
        return False

    def disconnect(self):
        pass

    def getValue(self):
        return None


def buildSensorParamsDict(
    read: bool = True, slope: float = 10, intercept: float = -10
) -> dict:
    return {
        SParams.NAME.value: "Test name",
        SParams.CHANNEL.value: 0,
        SParams.SERIAL.value: 0000,
        SParams.READ.value: read,
        SParams.CALIBRATION_SECTION.value: {
            SParams.SLOPE.value: slope,
            SParams.INTERCEPT.value: intercept,
        },
        SParams.PROPERTIES_SECTION.value: {
            "serial_number": "Y8888888",
            "max_weight": "150 kg",
        },
    }


def setupSensor(sensor: Sensor, id: str, read: bool, driver: Driver) -> Sensor:
    sensor.setup(id, buildSensorParamsDict(read), driver)


@pytest.fixture
def sensor_av() -> Sensor:
    sensor = Sensor()
    setupSensor(sensor, "test_id", True, AvailableDriverMock)
    return sensor


@pytest.fixture
def sensor_av_nr() -> Sensor:
    sensor = Sensor()
    setupSensor(sensor, "test_id", False, AvailableDriverMock)
    return sensor


@pytest.fixture
def sensor_unav() -> Sensor:
    sensor = Sensor()
    setupSensor(sensor, "test_id", True, UnavailableDriverMock)
    return sensor


@pytest.fixture
def sensor_unav_nr() -> Sensor:
    sensor = Sensor()
    setupSensor(sensor, "test_id", False, UnavailableDriverMock)
    return sensor


# Tests


def test_available_noread_sensor_connect(sensor_av_nr: Sensor) -> None:
    sensor_av_nr.connect(check=True)
    assert sensor_av_nr.getStatus() == SStatus.IGNORED


def test_available_read_sensor_connect(sensor_av: Sensor) -> None:
    sensor_av.connect(check=True)
    assert sensor_av.getStatus() == SStatus.AVAILABLE


def test_unavailable_noread_sensor_connect(sensor_unav_nr: Sensor) -> None:
    sensor_unav_nr.connect(check=True)
    assert sensor_unav_nr.getStatus() == SStatus.IGNORED


def test_unavailable_read_sensor_connect(sensor_unav: Sensor) -> None:
    sensor_unav.connect(check=True)
    assert sensor_unav.getStatus() == SStatus.NOT_FOUND


def test_available_read_unchecked_sensor_connection(sensor_av: Sensor) -> None:
    sensor_av.connect()
    assert sensor_av.getStatus() == SStatus.IGNORED


def test_available_read_checked_sensor_connection(sensor_av: Sensor) -> None:
    sensor_av.checkConnection()
    sensor_av.connect()
    assert sensor_av.getStatus() == SStatus.AVAILABLE


def test_available_sensor_register_values(sensor_av: Sensor) -> None:
    sensor_av.checkConnection()
    sensor_av.connect()
    sensor_av.registerValue()
    sensor_av.registerValue()
    assert sensor_av.getValues() == [10, 10]


def test_unavailable_sensor_register_values(sensor_unav: Sensor) -> None:
    sensor_unav.checkConnection()
    sensor_unav.connect()
    sensor_unav.registerValue()
    sensor_unav.registerValue()
    assert sensor_unav.getValues() == []


def test_available_sensor_calibration_values(sensor_av: Sensor) -> None:
    sensor_av.checkConnection()
    sensor_av.connect()
    sensor_av.registerValue()
    sensor_av.registerValue()
    assert sensor_av.getCalibValues() == [90, 90]


def test_available_sensor_clear_registered_values(sensor_av: Sensor) -> None:
    sensor_av.checkConnection()
    sensor_av.connect()
    sensor_av.registerValue()
    sensor_av.registerValue()
    sensor_av.clearValues()
    assert sensor_av.getValues() == []


def test_sensor_modify_calibration_params(sensor_av: Sensor) -> None:
    sensor_av.setSlope(100)
    sensor_av.setIntercept(-50)
    calib_params = sensor_av.getSlopeIntercept()
    assert calib_params == [100, -50]


def test_sensor_modify_read_status(sensor_av: Sensor) -> None:
    sensor_av.setRead(read=False)
    assert not sensor_av.getIsReadable()
