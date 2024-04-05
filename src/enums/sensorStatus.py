from enum import Enum
from src.enums.qssLabels import QssLabels
from src.enums.uiResources import IconPaths


class SStatus(Enum):
    IGNORED = (IconPaths.STATUS_OFF, QssLabels.SENSOR_IGNORED)
    AVAILABLE = (IconPaths.STATUS_OK, QssLabels.SENSOR_OK)
    NOT_FOUND = (IconPaths.STATUS_ERROR, QssLabels.SENSOR_ERROR)


class SGStatus(Enum):
    IGNORED = (IconPaths.STATUS_OFF, QssLabels.SENSOR_GROUP_IGNORED)
    OK = (IconPaths.STATUS_OK, QssLabels.SENSOR_GROUP_OK)
    WARNING = (IconPaths.STATUS_WARN, QssLabels.SENSOR_GROUP_WARN)
    ERROR = (IconPaths.STATUS_ERROR, QssLabels.SENSOR_GROUP_ERROR)
