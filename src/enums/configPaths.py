from enum import Enum


class ConfigPaths(Enum):
    # Settings
    CONFIG_NAME = "settings.config.name"
    CONFIG_VERSION = "settings.config.version"

    TEST_NAME = "settings.test.name"

    RECORD_INTERVAL_MS = "settings.recording.data_interval_ms"
    RECORD_TARE_AMOUNT = "settings.recording.tare_data_amount"

    # Sensors
    SENSOR_GROUPS_SECTION = "sensor_groups"
    SENSORS_SECTION = "sensors"
