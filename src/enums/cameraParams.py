from enum import Enum


# Camera params
class CParams(Enum):
    # Config sections
    CONNECTION_SECTION = "connection"
    SETTINGS_SECTION = "settings"
    PROPERTIES_SECTION = "properties"

    # Config params paths
    NAME = "name"
    TYPE = "type"
    READ = "read"
    CHANNEL = "channel"
    SERIAL = "serial"
    FRAME_WIDTH = "frame_width"
    FRAME_HEIGHT = "frame_height"
    FPS = "fps"

    # Handler additional params
    STATUS = "status"
    SENSOR = "camera"
    VALUE = "value"
