from enum import Enum


class SensorStatus(Enum):
    IGNORED = 'gray'
    AVAILABLE = 'green'
    NOT_FOUND = 'red'
