from enum import Enum


class SStatus(Enum):
    IGNORED = "Ignored"
    AVAILABLE = "Connected"
    NOT_FOUND = "Not found"


class SGStatus(Enum):
    IGNORED = "Sensor group ignored"
    OK = "All sensors connected"
    WARNING = "Some sensors not found"
    ERROR = "All sensors not found"
