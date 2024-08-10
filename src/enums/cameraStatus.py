from enum import Enum
from src.enums.qssLabels import QssLabels
from src.enums.uiResources import IconPaths


class CStatus(Enum):
    IGNORED = (IconPaths.STATUS_OFF, QssLabels.SENSOR_GROUP_IGNORED)
    AVAILABLE = (IconPaths.STATUS_OK, QssLabels.SENSOR_GROUP_OK)
    NOT_FOUND = (IconPaths.STATUS_ERROR, QssLabels.SENSOR_GROUP_ERROR)
