[:house: `Back to Home`](../home.md)

# Config File

Config main content:
- [General settings](#general-settings)
- [Platform 1 loadcell list](#platform-1-loadcell-list)
- [Platform 2 loadcell list](#platform-2-loadcell-list)
- [Encoder list](#encoder-list)
- [IMU list](#imu-list)
- [Calibration sensor](#calibration-sensor)

## General settings

https://github.com/AaronPB/force_platform/blob/4042350c678310280ec6b3abcc6ddf7684dfab5c/config.yaml#L1-L21

Information of all the keys involved in this config section:

| Key | Type | Description |
| :--- | :---: | :--- |
| `custom_config_path` | STRING | Custom config to load instead of this default config. Set to `null` if the default config is needed. |
| `calibration_times.data_interval_ms` | INT | Data recording frequency (in ms). |
| `calibration_times.calibration_time_ms` | INT | Data recording duration (in ms). |
| `test_times.data_interval_ms` | INT | Data recording frequency (in ms). |
| `test_times.tare_time_ms` | INT | Data recording duration to tare (in ms). |
| `test_results.folder` | STRING | Path to desired folder where the `csv` files will be saved. |
| `test_results.name` | STRING | Name of the generated `csv` files. |
| `test_results.save_calib_results` | BOOL | Save file with calibrated values defined in `config`. |
| `test_results.save_raw_results` | BOOL | Save file without calibrated values. A `_RAW` suffix will be added to the file name. |
| `tab_plotters.enabled` | BOOL | Enables plot thread process. |
| `tab_plotters.update_interval_ms` | INT | Plot refresh rate (in ms). With lower values it could have impact in recording data. |
| `tab_plotters.plot_max_values.platform_forces` | INT | Maximum values to be displayed in platform force plots. |
| `tab_plotters.plot_max_values.platform_stabilogram` | INT | Maximum values to be displayed in platform stabilogram plots. |
| `tab_plotters.plot_max_values.encoders` | INT | Maximum values to be displayed in encoder plots. |
| `tab_plotters.plot_max_values.imu_angles` | INT | Maximum values to be displayed in imu angle plots. |

## Platform 1 loadcell list
Declare the amount of Phidget loadcells in the first platform.

https://github.com/AaronPB/force_platform/blob/4042350c678310280ec6b3abcc6ddf7684dfab5c/config.yaml#L22-L33

Information of all the keys involved in this config section:

| Key | Type | Description |
| :---: | :---: | :--- |
| `load_cell_x` | STRING | ID of load cell section. |
| `name` | STRING | Load cell name. |
| `channel` | INT | Channel number (0 to 3) in Phidget device. |
| `serial` | INT | USB serial number of Phidget device. |
| `read_data` | BOOL | Enable or disable loadcell data recording. Can be modified in GUI. |
| `properties` | - | (Could be empty) Configuration section where you can provide more information about the loadcell. This will be shown in calibration section. |
| `calibration_data.m` | INT | Slope parameter. |
| `calibration_data.b` | INT | Intercept parameter. |

## Platform 2 loadcell list
Declare the amount of Phidget loadcells in the second platform.

https://github.com/AaronPB/force_platform/blob/4042350c678310280ec6b3abcc6ddf7684dfab5c/config.yaml#L155-L166

The config section keys are the same as in [Platform 1 loadcell list](#platform-1-loadcell-list).

## Encoder list
Declare the amount of Phidget encoders.

https://github.com/AaronPB/force_platform/blob/4042350c678310280ec6b3abcc6ddf7684dfab5c/config.yaml#L288-L300

Information of all the keys involved in this config section:

| Key | Type | Description |
| :---: | :---: | :--- |
| `encoder_x` | STRING | ID of encoder section. |
| `name` | STRING | Encoder name. |
| `channel` | INT | Channel number (0 to 3) in Phidget device. |
| `serial` | INT | USB serial number of Phidget device. |
| `read_data` | BOOL | Enable or disable encoder data recording. Can be modified in GUI. |
| `initial_position` | INT | The initial value of the encoder state. The sensor generates incremental values. |
| `properties` | - | (Could be empty) Configuration section where you can provide more information. This will be shown in calibration section. |
| `calibration_data.m` | INT | Slope parameter. |
| `calibration_data.b` | INT | Intercept parameter. |

## IMU list
Declare the amount of Taobotics IMUs.

https://github.com/AaronPB/force_platform/blob/4042350c678310280ec6b3abcc6ddf7684dfab5c/config.yaml#L313-L319

Information of all the keys involved in this config section:

| Key | Type | Description |
| :---: | :---: | :--- |
| `imu_x` | STRING | ID of IMU section. |
| `name` | STRING | IMU name. |
| `serial` | STRING | Absolute USB path. Use `ll /dev/serial/by-path/`. |
| `read_data` | BOOL | Enable or disable IMU data recording. Can be modified in GUI. |
| `properties` | - | (Could be empty) Configuration section where you can provide more information. This will be shown in calibration section. |

## Calibration sensor
Define here a Phidget loadcell that will be used for reference data when calibrating, instead of manual inputs.

https://github.com/AaronPB/force_platform/blob/4042350c678310280ec6b3abcc6ddf7684dfab5c/config.yaml#L332-L342

The config section keys are similar as in [Platform 1 loadcell list](#platform-1-loadcell-list).

---

[:house: `Back to Home`](../home.md)