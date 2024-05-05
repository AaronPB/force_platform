from enum import Enum, auto


# Sensor types
class STypes(Enum):
    SENSOR_LOADCELL = auto()
    SENSOR_ENCODER = auto()
    SENSOR_IMU = auto()


# Sensor group types
class SGTypes(Enum):
    GROUP_DEFAULT = auto()
    GROUP_PLATFORM = auto()
