from enum import Enum


class ConfigPaths(Enum):
    GENERAL_CUSTOM_CONFIG_PATH = "general_settings.custom_config_path"

    GENERAL_CALIBRATION_INTERVAL_MS = (
        "general_settings.calibration_times.data_interval_ms"
    )
    GENERAL_CALIBRATION_DURATION_MS = (
        "general_settings.calibration_times.calibration_time_ms"
    )
    GENERAL_TEST_INTERVAL_MS = "general_settings.test_times.data_interval_ms"
    GENERAL_TARE_DURATION_MS = "general_settings.test_times.tare_time_ms"

    GENERAL_TEST_FOLDER = "general_settings.test_results.folder"
    GENERAL_TEST_NAME = "general_settings.test_results.name"
    GENERAL_TEST_SAVE_CALIB = "general_settings.test_results.save_calib_results"
    GENERAL_TEST_SAVE_RAW = "general_settings.test_results.save_raw_results"

    GENERAL_PLOTTERS_ENABLED = "general_settings.tab_plotters.enabled"
    GENERAL_PLOTTERS_INTERVAL_MS = "general_settings.tab_plotters.update_interval_ms"
    GENERAL_PLOTTERS_MAX_FORCES = (
        "general_settings.tab_plotters.plot_max_values.platform_forces"
    )
    GENERAL_PLOTTERS_MAX_STABILOGRAM = (
        "general_settings.tab_plotters.plot_max_values.platform_stabilogram"
    )
    GENERAL_PLOTTERS_MAX_ENCODERS = (
        "general_settings.tab_plotters.plot_max_values.encoders"
    )
    GENERAL_PLOTTERS_MAX_IMUS = (
        "general_settings.tab_plotters.plot_max_values.imu_angles"
    )

    PHIDGET_P1_LOADCELL_CONFIG_SECTION = "p1_phidget_loadcell_list"
    PHIDGET_P2_LOADCELL_CONFIG_SECTION = "p2_phidget_loadcell_list"
    PHIDGET_ENCODER_CONFIG_SECTION = "phidget_encoder_list"
    TAOBOTICS_IMU_CONFIG_SECTION = "taobotics_imu_list"
    CALIBRATION_CONFIG_SECTION = "calibration_sensor"
