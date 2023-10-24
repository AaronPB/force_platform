from enum import Enum


class ConfigPaths(Enum):
    GENERAL_CUSTOM_CONFIG_PATH = 'general_settings.custom_config_path'

    GENERAL_CALIBRATION_INTERVAL_MS = 'general_settings.calibration_times.data_interval_ms'
    GENERAL_CALIBRATION_DURATION_MS = 'general_settings.calibration_times.recording_ms'
    GENERAL_TEST_INTERVAL_MS = 'general_settings.test_times.data_interval_ms'
    GENERAL_TARE_DURATION_MS = 'general_settings.test_times.tare_recording_ms'

    GENERAL_TEST_FOLDER = 'general_settings.test_file_path.folder'
    GENERAL_TEST_NAME = 'general_settings.test_file_path.name'

    PHIDGET_P1_LOADCELL_CONFIG_SECTION = 'p1_phidget_loadcell_list'
    PHIDGET_P2_LOADCELL_CONFIG_SECTION = 'p2_phidget_loadcell_list'
    PHIDGET_ENCODER_CONFIG_SECTION = 'phidget_encoder_list'
    TAOBOTICS_IMU_CONFIG_SECTION = 'taobotics_imu_list'
    CALIBRATION_CONFIG_SECTION = 'calibration_sensor'
