# -*- coding: utf-8 -*-

from src.handlers.sensorGroup import SensorGroup
from src.enums.sensorStatus import SensorStatus as SStatus
import pytest


# General mocks, builders and fixtures


class SensorMock:
    def __init__(
        self,
        id: str = "sensor_id",
        status: SStatus = SStatus.AVAILABLE,
        readable: bool = True,
    ) -> None:
        self.id = id
        self.status = status
        self.readable = readable
        self.connection_checked = False
        self.intercept = 10

    def checkConnection(self) -> bool:
        self.connection_checked = True
        return self.status == SStatus.AVAILABLE

    def connect(self) -> bool:
        if self.connection_checked:
            return self.status == SStatus.AVAILABLE
        return False

    def disconnect(self) -> None:
        pass

    def setIntercept(self, intercept: float) -> None:
        self.intercept = intercept

    def getName(self) -> str:
        return "Sensor name"

    def getProperties(self) -> str:
        return "Properties example"

    def getStatus(self) -> SStatus:
        return self.status

    def getIsReadable(self) -> bool:
        return self.readable

    def getSlopeIntercept(self) -> list[float]:
        return [1, self.intercept]


@pytest.fixture
def sensor_group_single() -> SensorGroup:
    sensor_group = SensorGroup("Sensor Group Test")
    # sensor = Sensor()
    # setupSensor(sensor, True, AvailableDriverMock)
    sensor_group.addSensor(SensorMock())
    return sensor_group


@pytest.fixture
def sensor_group_filled() -> SensorGroup:
    """
    Sensor group filled with 2 available and 2 unavailable sensors
    """
    sensor_group = SensorGroup("Sensor Group Test")
    for i in range(1, 3):
        sensor_id = f"sensor_{i}"
        sensor_group.addSensor(SensorMock(id=sensor_id, status=SStatus.AVAILABLE))
    for i in range(3, 5):
        sensor_id = f"sensor_{i}"
        sensor_group.addSensor(SensorMock(id=sensor_id, status=SStatus.NOT_FOUND))
    return sensor_group


# Tests


def test_sensor_group_add() -> None:
    sensor_group = SensorGroup("Test")
    sensor_group.addSensor(SensorMock())
    assert sensor_group.getGroupSize() == 1


def test_sensor_group_status_start_unchecked(sensor_group_filled: SensorGroup) -> None:
    sensor_group_filled.start()
    assert not sensor_group_filled.getGroupIsActive()


def test_sensor_group_status_start(sensor_group_filled: SensorGroup) -> None:
    sensor_group_filled.checkConnections()
    sensor_group_filled.start()
    assert sensor_group_filled.getGroupIsActive()


def test_sensor_group_status_stop(sensor_group_filled: SensorGroup) -> None:
    sensor_group_filled.checkConnections()
    sensor_group_filled.start()
    sensor_group_filled.stop()
    assert not sensor_group_filled.getGroupIsActive()


def test_sensor_group_connections(sensor_group_filled: SensorGroup) -> None:
    connected = sensor_group_filled.checkConnections()
    assert connected


def test_sensor_group_info_size_match(sensor_group_filled: SensorGroup) -> None:
    assert len(sensor_group_filled.getGroupInfo()) == sensor_group_filled.getGroupSize()


def test_sensor_group_available_info_size(sensor_group_filled: SensorGroup) -> None:
    """
    Check dict size when getting only the available sensor information
    """
    sensor_group_filled.checkConnections()
    assert len(sensor_group_filled.getGroupAvailableInfo()) == 2


def test_sensor_group_tare(sensor_group_filled: SensorGroup) -> None:
    """
    Try to tare only sensor_1, having a mean value of 4.
    Mean should be 0, so new_intercept = old_intercept - measured_mean
    In this test case, it is simplified to: intercept = 10 - 4 = 6
    """
    mean_dict = {"sensor_1": 4}
    sensor_group_filled.tareSensors(mean_dict)
    calib_params = sensor_group_filled.sensors["sensor_1"].getSlopeIntercept()
    assert calib_params[1] == 6
