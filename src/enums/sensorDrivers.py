from enum import Enum
from handlers import drivers


class SensorDrivers(Enum):
    PHIDGET_LOADCELL_DRIVER = drivers.PhidgetLoadCell
    PHIDGET_ENCODER_DRIVER = drivers.PhidgetEncoder
    TAOBOTICS_IMU_DRIVER = drivers.TaoboticsIMU
