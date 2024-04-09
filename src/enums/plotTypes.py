from enum import Enum, auto


class PlotTypes(Enum):
    GROUP_PLATFORM_COP = auto()
    GROUP_PLATFORM_FORCES = auto()

    SENSOR_LOADCELL_FORCE = auto()
    SENSOR_ENCODER_DISTANCE = auto()
    SENSOR_IMU_ANGLES = auto()
    SENSOR_IMU_VELOCITY = auto()
    SENSOR_IMU_ACCELERATION = auto()
