from enum import Enum


class SensorParams(Enum):
    # Internal config params
    NAME = 'name'
    CHANNEL = 'channel'
    SERIAL = 'serial'
    READ = 'read_data'
    INITIAL_POS = 'initial_position'
    SLOPE = 'm'
    INTERCEPT = 'b'

    # Internal config sections
    CALIBRATION_SECTION = 'calibration_data'
    PROPERTIES_SECTION = 'properties'

    # Handler additional params
    STATUS = 'status'
    SENSOR = 'sensor'
    VALUE = 'value'
