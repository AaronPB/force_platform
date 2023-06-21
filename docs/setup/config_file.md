:house: <kbd>[Back to Home](../home.md)</kbd>

# Config File

Config main content:
- [General settings](#general-settings)
- [Platform 1 loadcell list](#platform-1-loadcell-list)
- [Platform 2 loadcell list](#platform-2-loadcell-list)
- [Encoder list](#encoder-list)
- [IMU list](#imu-list)
- [Calibration sensor](#calibration-sensor)

## General settings

https://github.com/AaronPB/force_platform/blob/88ecc364dc7c97f09efae3091a1ce522aba9c423/config.yaml#L1-L12

Information of all the keys involved in this config section:

| Key | Type | Description |
| :--- | :---: | :--- |
| `calibration_times.data_interval_ms` | INT | Data recording frequency (in ms). |
| `calibration_times.recording_time` | INT | Data recording duration (in ms). |
| `test_times.data_interval_ms` | INT | Data recording frequency (in ms). |
| `test_times.tare_time_ms` | INT | Duration of data recording to tare (in ms). |
| `test_file_path.folder` | STRING | Path to desired folder where the `csv` files will be saved. |
| `test_file_path.name` | STRING | Name of the generated `csv` files. |
| `test_results.generate_plots` | BOOL | Work in progress. |

## Platform 1 loadcell list
Declare the amount of Phidget loadcells in the first platform.

https://github.com/AaronPB/force_platform/blob/88ecc364dc7c97f09efae3091a1ce522aba9c423/config.yaml#L13-L24

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

https://github.com/AaronPB/force_platform/blob/88ecc364dc7c97f09efae3091a1ce522aba9c423/config.yaml#L146-L157

The config section keys are the same as in [Platform 1 loadcell list](#platform-1-loadcell-list).

## Encoder list
Declare the amount of Phidget encoders.

https://github.com/AaronPB/force_platform/blob/88ecc364dc7c97f09efae3091a1ce522aba9c423/config.yaml#L279-L291

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

https://github.com/AaronPB/force_platform/blob/88ecc364dc7c97f09efae3091a1ce522aba9c423/config.yaml#L304-L310

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

https://github.com/AaronPB/force_platform/blob/88ecc364dc7c97f09efae3091a1ce522aba9c423/config.yaml#L323-L333

The config section keys are similar as in [Platform 1 loadcell list](#platform-1-loadcell-list).

---

:house: <kbd>[Back to Home](../home.md)</kbd>