from enum import Enum


class ConfigPaths(Enum):
    # Settings
    CUSTOM_CONFIG_PATH = "settings.custom_config_path"

    TEST_NAME = "settings.test.name"
    TEST_FOLDER_PATH = "settings.test.folder_path"
    TEST_SAVE_RAW = "settings.test.results.save_raw"
    TEST_SAVE_CALIB = "settings.test.results.save_calib"

    RECORD_INTERVAL_MS = "settings.recording.data_interval_ms"
    RECORD_TARE_AMOUNT = "settings.recording.tare_data_amount"

    CALIBRATION_INTERVAL_MS = "settings.calibration.data_interval_ms"
    CALIBRATION_DATA_AMOUNT = "settings.calibration.data_amount"

    # Sensors
    SENSOR_GROUPS_SECTION = "sensor_groups"
    SENSORS_SECTION = "sensors"
    CALIBRATION_LOADCELL_SENSOR = "sensors_calibration.phidget_loadcell_reference"
    CALIBRATION_PLATFORM_TRIAXIAL = "sensors_calibration.platform_reference_triaxial"
