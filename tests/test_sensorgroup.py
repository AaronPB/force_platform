# -*- coding: utf-8 -*-

from src.handlers.sensorGroup import SensorGroup
from src.enums.sensorStatus import SStatus, SGStatus
from src.enums.sensorTypes import SGTypes, STypes
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
        self.values: list = []

    def connect(self) -> bool:
        if self.connection_checked:
            return self.status == SStatus.AVAILABLE
        return False

    def disconnect(self) -> None:
        pass

    def checkConnection(self) -> bool:
        self.connection_checked = True
        return self.status == SStatus.AVAILABLE

    def registerValue(self) -> None:
        if self.status is not SStatus.AVAILABLE:
            return
        self.values.append(10)

    def getStatus(self) -> SStatus:
        return self.status

    def getType(self) -> STypes:
        return STypes.SENSOR_LOADCELL

    def clearValues(self) -> None:
        self.values.clear()

    def getValues(self) -> list:
        return self.values


@pytest.fixture
def sensor_group_single() -> SensorGroup:
    sensor_group = SensorGroup(
        id="group_id", name="Sensor Group Test", type=SGTypes.GROUP_DEFAULT
    )
    sensor_group.addSensor(SensorMock())
    return sensor_group


@pytest.fixture
def sensor_group_filled() -> SensorGroup:
    """
    Sensor group filled with 2 available and 2 unavailable sensors
    """
    sensor_group = SensorGroup(
        id="group_id", name="Sensor Group Test", type=SGTypes.GROUP_DEFAULT
    )
    sensor_group.setRead(read=True)
    for i in range(1, 3):
        sensor_id = f"sensor_{i}"
        sensor_group.addSensor(SensorMock(id=sensor_id, status=SStatus.AVAILABLE))
    for i in range(3, 5):
        sensor_id = f"sensor_{i}"
        sensor_group.addSensor(SensorMock(id=sensor_id, status=SStatus.NOT_FOUND))
    return sensor_group


@pytest.fixture
def sensor_group_filled_av() -> SensorGroup:
    """
    Sensor group filled with 4 available sensors
    """
    sensor_group = SensorGroup(
        id="group_id", name="Sensor Group Test", type=SGTypes.GROUP_DEFAULT
    )
    sensor_group.setRead(read=True)
    for i in range(1, 5):
        sensor_id = f"sensor_{i}"
        sensor_group.addSensor(SensorMock(id=sensor_id, status=SStatus.AVAILABLE))
    return sensor_group


@pytest.fixture
def sensor_group_filled_unav() -> SensorGroup:
    """
    Sensor group filled with 4 unavailable sensors
    """
    sensor_group = SensorGroup(
        id="group_id", name="Sensor Group Test", type=SGTypes.GROUP_DEFAULT
    )
    sensor_group.setRead(read=True)
    for i in range(1, 5):
        sensor_id = f"sensor_{i}"
        sensor_group.addSensor(SensorMock(id=sensor_id, status=SStatus.NOT_FOUND))
    return sensor_group


# Tests


def test_check_group_id(sensor_group_single: SensorGroup) -> None:
    assert sensor_group_single.getID() == "group_id"


def test_check_group_name(sensor_group_single: SensorGroup) -> None:
    assert sensor_group_single.getName() == "Sensor Group Test"


def test_check_group_type(sensor_group_single: SensorGroup) -> None:
    assert sensor_group_single.getType() == SGTypes.GROUP_DEFAULT


def test_check_group_size(sensor_group_single: SensorGroup) -> None:
    assert sensor_group_single.getSize() == 1


def test_check_group_read(sensor_group_single: SensorGroup) -> None:
    assert sensor_group_single.getRead() == False


def test_check_group_status(sensor_group_single: SensorGroup) -> None:
    assert sensor_group_single.getStatus() == SGStatus.IGNORED


def test_check_group_active(sensor_group_single: SensorGroup) -> None:
    assert sensor_group_single.isActive() == False


def test_group_add(sensor_group_single: SensorGroup) -> None:
    sensor_group_single.addSensor(SensorMock(id="sensor_id_2"))
    assert sensor_group_single.getSize() == 2


def test_group_connections(sensor_group_filled: SensorGroup) -> None:
    assert sensor_group_filled.checkConnections() == True


def test_group_connections_status_no_read(sensor_group_single: SensorGroup) -> None:
    sensor_group_single.checkConnections()
    assert sensor_group_single.getStatus() == SGStatus.IGNORED


def test_group_connections_status_all_available(
    sensor_group_filled_av: SensorGroup,
) -> None:
    sensor_group_filled_av.checkConnections()
    assert sensor_group_filled_av.getStatus() == SGStatus.OK


def test_group_connections_status_any_available(
    sensor_group_filled: SensorGroup,
) -> None:
    sensor_group_filled.checkConnections()
    assert sensor_group_filled.getStatus() == SGStatus.WARNING


def test_group_connections_status_none_available(
    sensor_group_filled_unav: SensorGroup,
) -> None:
    sensor_group_filled_unav.checkConnections()
    assert sensor_group_filled_unav.getStatus() == SGStatus.ERROR


def test_group_status_start_unchecked(sensor_group_filled: SensorGroup) -> None:
    sensor_group_filled.start()
    assert sensor_group_filled.isActive() == False


def test_group_status_start(sensor_group_filled: SensorGroup) -> None:
    sensor_group_filled.checkConnections()
    sensor_group_filled.start()
    assert sensor_group_filled.isActive() == True


def test_group_status_stop(sensor_group_filled: SensorGroup) -> None:
    sensor_group_filled.checkConnections()
    sensor_group_filled.start()
    sensor_group_filled.stop()
    assert sensor_group_filled.isActive() == False


def test_group_available_sensors_size(sensor_group_filled: SensorGroup) -> None:
    """
    Check dict size when getting only the available sensor information
    """
    sensor_group_filled.checkConnections()
    assert len(sensor_group_filled.getSensors(only_available=True)) == 2


def test_group_available_type_sensors_size(sensor_group_filled: SensorGroup) -> None:
    """
    Check dict size when getting only the available sensor type information
    """
    sensor_group_filled.checkConnections()
    assert (
        len(
            sensor_group_filled.getSensors(
                only_available=True, sensor_type=STypes.SENSOR_IMU
            )
        )
        == 0
    )


def test_group_register_values(sensor_group_filled: SensorGroup) -> None:
    sensor_group_filled.checkConnections()
    sensor_group_filled.start()
    sensor_group_filled.register()
    sensor_group_filled.register()
    sensor_group_filled.stop()
    sensor_dict = sensor_group_filled.getSensors()
    assert sensor_dict["sensor_1"].getValues() == [10, 10]


def test_group_clear_values(sensor_group_filled: SensorGroup) -> None:
    sensor_group_filled.checkConnections()
    sensor_group_filled.start()
    sensor_group_filled.register()
    sensor_group_filled.register()
    sensor_group_filled.stop()
    sensor_group_filled.clearValues()
    sensor_dict = sensor_group_filled.getSensors()
    assert sensor_dict["sensor_1"].getValues() == []


def test_group_modify_read_status(sensor_group_filled: SensorGroup) -> None:
    sensor_group_filled.setRead(False)
    assert sensor_group_filled.getRead() == False
