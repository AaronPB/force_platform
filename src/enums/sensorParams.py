from enum import Enum


# Sensor params
class SParams(Enum):
    # Config sections
    CONNECTION_SECTION = "connection"
    CALIBRATION_SECTION = "calibration"
    PROPERTIES_SECTION = "properties"

    # Config params paths
    NAME = "name"
    TYPE = "type"
    READ = "read"
    CHANNEL = "channel"
    SERIAL = "serial"
    SLOPE = "slope"
    INTERCEPT = "intercept"
    INITIAL_POS = "initial_position"

    # Handler additional params
    STATUS = "status"
    SENSOR = "sensor"
    VALUE = "value"


# Sensor group params
class SGParams(Enum):
    NAME = "name"
    TYPE = "type"
    READ = "read"
    SENSOR_LIST = "sensor_list"
