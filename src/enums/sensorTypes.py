from enum import Enum, auto
from handlers import drivers


# Sensor types
class STypes(Enum):
    SENSOR_LOADCELL = drivers.PhidgetLoadCell
    SENSOR_ENCODER = drivers.PhidgetEncoder
    SENSOR_IMU = drivers.TaoboticsIMU


# Sensor group types
class SGTypes(Enum):
    GROUP_PLATFORM = auto()
    GROUP_GENERIC = auto()
