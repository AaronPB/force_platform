from enum import Enum


# Sensor types
class STypes(Enum):
    SENSOR_LOADCELL = "Load Cell"
    SENSOR_ENCODER = "Encoder"
    SENSOR_IMU = "IMU"


# Sensor group types
class SGTypes(Enum):
    GROUP_DEFAULT = "Default"
    GROUP_PLATFORM = "Platform"
