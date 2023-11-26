from enum import Enum
from src.enums.qssLabels import QssLabels


class SensorStatus(Enum):
    IGNORED = None
    AVAILABLE = QssLabels.SENSOR_CONNECTED
    NOT_FOUND = QssLabels.SENSOR_NOT_CONNECTED
