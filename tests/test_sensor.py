# -*- coding: utf-8 -*-

from src.handlers.sensor import Sensor, Driver
from src.enums.sensorStatus import SStatus
from src.enums.sensorParams import SParams
from src.enums.sensorTypes import STypes
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


def buildSensorParamsDict(
    read: bool = True, slope: float = 10, intercept: float = -10
) -> dict:
    return {
        SParams.NAME.value: "Test name",
        SParams.READ.value: read,
        SParams.TYPE.value: "SENSOR_LOADCELL",
        SParams.CONNECTION_SECTION.value: {
            SParams.SERIAL.value: 0,
            SParams.CHANNEL.value: 0000,
        },
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
def sensor_unav() -> Sensor:
    sensor = Sensor()
    setupSensor(sensor, "test_id", True, UnavailableDriverMock)
    return sensor


# Tests


def test_check_sensor_id(sensor_av: Sensor) -> None:
    assert sensor_av.getID() == "test_id"


def test_check_sensor_name(sensor_av: Sensor) -> None:
    assert sensor_av.getName() == "Test name"


def test_check_sensor_type(sensor_av: Sensor) -> None:
    assert sensor_av.getType() == STypes.SENSOR_LOADCELL


def test_check_sensor_read(sensor_av: Sensor) -> None:
    assert sensor_av.getRead() == True


def test_check_sensor_status(sensor_av: Sensor) -> None:
    assert sensor_av.getStatus() == SStatus.IGNORED


def test_check_sensor_properties(sensor_av: Sensor) -> None:
    assert sensor_av.getProperties() == " - Y8888888 - 150 kg - "


def test_check_sensor_slope(sensor_av: Sensor) -> None:
    assert sensor_av.getSlope() == 10


def test_check_sensor_intercept(sensor_av: Sensor) -> None:
    assert sensor_av.getIntercept() == -10


sensor_cases = [
    ("test_id", True, AvailableDriverMock, SStatus.AVAILABLE),
    ("test_id", False, AvailableDriverMock, SStatus.IGNORED),
    ("test_id", True, UnavailableDriverMock, SStatus.NOT_FOUND),
    ("test_id", False, UnavailableDriverMock, SStatus.IGNORED),
]


@pytest.mark.parametrize("sensor_status", sensor_cases)
@pytest.mark.parametrize("check_connection", [True, False])
def test_sensor_connection(sensor_status, check_connection: bool) -> None:
    sensor = Sensor()
    id, read, driver, expected_status = sensor_status
    setupSensor(sensor, id, read, driver)
    sensor.connect(check=check_connection)
    if check_connection:
        assert sensor.getStatus() == expected_status
    else:
        assert sensor.getStatus() == SStatus.IGNORED


def test_unchecked_sensor_connection(sensor_av: Sensor) -> None:
    sensor_av.connect()
    assert sensor_av.getStatus() == SStatus.IGNORED


def test_checked_sensor_connection(sensor_av: Sensor) -> None:
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


def test_clear_registered_values(sensor_av: Sensor) -> None:
    sensor_av.checkConnection()
    sensor_av.connect()
    sensor_av.registerValue()
    sensor_av.registerValue()
    sensor_av.clearValues()
    assert sensor_av.getValues() == []


def test_sensor_modify_read_status(sensor_av: Sensor) -> None:
    sensor_av.setRead(read=False)
    assert sensor_av.getRead() == False


def test_sensor_modify_slope_param(sensor_av: Sensor) -> None:
    sensor_av.setSlope(slope=20.5)
    assert sensor_av.getSlope() == 20.5


def test_sensor_modify_intercept_param(sensor_av: Sensor) -> None:
    sensor_av.setIntercept(intercept=-2.5)
    assert sensor_av.getIntercept() == -2.5
