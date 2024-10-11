import streamlit as st


def homePage():
    _, img_col, _ = st.columns([0.2, 0.6, 0.2])
    img_col.image(
        image="images/force_platform_logo.png",
        use_column_width=True,
    )
    st.title("Welcome to Force Platform Reader")
    st.write(
        "Check the following documentation if you are not familiar with the application."
    )

    st.header("Settings page")

    with st.expander("Load a custom config file", icon=":material/upload_file:"):
        st.write("You can load a custom configuration file.")
        with open("config.yaml", "r") as file:
            config_file = file.read()
        st.download_button(
            label="Download the default config file",
            key="download_button_default_config",
            type="secondary",
            use_container_width=True,
            file_name="config.yaml",
            help="Download the default config file to customize it",
            data=config_file,
            mime="text/yaml",
        )
        st.subheader("Configuration structure")
        st.markdown(
            """
            The configuration file follows a certain structure in order to be loaded correctly.
            
            - All sensors must be defined under the `sensors` configuration section.
            - To register data from a sensor, its `id` needs to be included in a `sensor_list` of a defined sensor group, under the `sensor_groups` configuration section.
            """
        )
        st.warning(
            "Sensors that are not included in a `sensor_list` are ignored and not loaded.",
            icon=":material/warning:",
        )
        st.info(
            "There are some requirements for certain sensor and group types. Check the info below.",
            icon=":material/info:",
        )
        code_config_struct = """
            %YAML 1.2.2
            general_settings:
              config:
                name: Custom config
                version: 2.0
              recording:
                data_interval_ms: 10
                tare_data_amount: 300
            sensor_groups:
              group_id:
                name: Group name
                type: GROUP_TYPE
                read: true
                sensor_list: [sensor_id]
            sensors:
              sensor_id:
                name: Sensor name
                type: SENSOR_TYPE
                read: true
                connection:
                  channel: 0
                  serial: path/to/usb
                properties: []
                calibration:
                  slope: 1
                  intercept: 0
            """
        st.code(code_config_struct, language="yaml")
        # Sensor types
        st.subheader("Sensor types")

        sensor_tab_loadcell, sensor_tab_encoder, sensor_tab_imu = st.tabs(
            ["`SENSOR_LOADCELL`", "`SENSOR_ENCODER`", "`SENSOR_IMU`"]
        )
        ## Loadcell sensors
        sensor_loadcell_col_1, sensor_loadcell_col_2 = sensor_tab_loadcell.columns(2)
        sensor_loadcell_col_1.markdown(
            """
            #### Section example

            ```yaml
            name: P1_LoadCell_Z_1
            type: SENSOR_LOADCELL
            read: true
            connection:
              channel: 0
              serial: 583477
            properties: []
            calibration:
              slope: 1460645.82
              intercept: 0
            ```
            """
        )
        sensor_loadcell_col_2.markdown(
            """
            #### Compatible sensors

            All sensors that are compatible with the [PhidgetBridge 4-input](https://www.phidgets.com/?tier=3&catid=98&pcid=78&prodid=1027).

            It has been tested with the following sensors:
            - [Zemic L6P Planar Load Cell](https://www.zemiceurope.com/es/categories/celulas-de-carga/l6p.html) (main sensors).
            - [Phidgets S-Type Load Cell](https://www.phidgets.com/?tier=3&catid=9&pcid=7&prodid=229)
            - [Phidgets Single Point Load Cell](https://www.phidgets.com/?tier=3&catid=9&pcid=7&prodid=226)
            """
        )
        sensor_tab_loadcell.markdown(
            """
            Required keys information:

            | Key | Type | Description |
            | :--- | :---: | :--- |
            | `name` | STRING | Sensor name. |
            | `type` | STRING | Sensor type: `SENSOR_LOADCELL`. |
            | `read` | BOOL | Enable or disable sensor data recording. Can be modified in GUI. |
            | `connection.channel` | INT | Channel number (0 to 3) in Phidget device. |
            | `connection.serial` | INT | USB serial number of Phidget device. |
            | `properties` | - | (Could be empty) Configuration section where you can provide more information. |
            | `calibration.slope` | INT | Slope parameter. |
            | `calibration.intercept` | INT | Intercept parameter. |
            """
        )
        ## Encoder sensors
        sensor_encoder_col_1, sensor_encoder_col_2 = sensor_tab_encoder.columns(2)
        sensor_encoder_col_1.markdown(
            """
            #### Section example

            ```yaml
            name: Encoder_Z_1
            type: SENSOR_ENCODER
            read: true
            connection:
              channel: 0
              serial: 641800
            initial_position: 0
            properties: []
            calibration:
              slope: 0.01875
              intercept: 0.0
            ```
            """
        )
        sensor_encoder_col_2.markdown(
            """
            #### Compatible sensors

            All sensors that are compatible with the [PhidgetEncoder HighSpeed 4-input](https://www.phidgets.com/?tier=3&catid=4&pcid=2&prodid=1199).
            
            It has been tested with the following sensors:
            - [Draw Wire Encoder](https://www.phidgets.com/?prodid=1001) (main sensors).
            """
        )
        sensor_tab_encoder.markdown(
            """
            Required keys information:

            | Key | Type | Description |
            | :--- | :---: | :--- |
            | `name` | STRING | Sensor name. |
            | `type` | STRING | Sensor type: `SENSOR_ENCODER`. |
            | `read` | BOOL | Enable or disable sensor data recording. Can be modified in GUI. |
            | `connection.channel` | INT | Channel number (0 to 3) in Phidget device. |
            | `connection.serial` | INT | USB serial number of Phidget device. |
            | `initial_position` | INT | The initial value of the encoder state. The sensor generates incremental values. |
            | `properties` | - | (Could be empty) Configuration section where you can provide more information. |
            | `calibration.slope` | INT | Slope parameter. |
            | `calibration.intercept` | INT | Intercept parameter. |
            """
        )
        ## IMU sensors
        sensor_imu_col_1, sensor_imu_col_2 = sensor_tab_imu.columns(2)
        sensor_imu_col_1.markdown(
            """
            #### Section example

            ```yaml
            name: IMU_Leg_Right
            type: SENSOR_IMU
            read: true
            connection:
              serial: /dev/serial/by-path/pci-0000:00:14.0-usb-0:1.1.4.3:1.0-port0
            properties:
              tag: IMU_1
            ```
            """
        )
        sensor_imu_col_2.markdown(
            """
            #### Compatible sensors

            The current version only supports [Taobotics IMUs](https://www.taobotics.com/).
            """
        )
        sensor_tab_imu.markdown(
            """
            Required keys information:

            | Key | Type | Description |
            | :--- | :---: | :--- |
            | `name` | STRING | Sensor name. |
            | `type` | STRING | Sensor type: `SENSOR_IMU`. |
            | `read` | BOOL | Enable or disable sensor data recording. Can be modified in GUI. |
            | `connection.serial` | STRING | Absolute USB path. Use `ll /dev/serial/by-path/`. |
            | `properties` | - | (Could be empty) Configuration section where you can provide more information. |
            """
        )

        st.subheader("Sensor group types")

        group_tab_default, group_tab_platform = st.tabs(
            ["`GROUP_DEFAULT`", "`GROUP_PLATFORM`"]
        )
        ## Default group
        group_default_col_1, group_default_col_2 = group_tab_default.columns(2)
        group_default_col_1.markdown(
            """
            #### Section example

            ```yaml
            name: Body IMUs
            type: GROUP_DEFAULT
            read: true
            sensor_list:
            - imu_1
            - imu_2
            - imu_3
            ```
            """
        )
        group_default_col_2.markdown(
            """
            #### Group description

            This group can be defined with multiple sensors.
            """
        )
        group_tab_default.markdown(
            """
            Information of all the keys involved in this config section:

            | Key | Type | Description |
            | :--- | :---: | :--- |
            | `name` | STRING | Group name. |
            | `type` | STRING | Group type: `GROUP_DEFAULT` or `GROUP_PLATFORM`. |
            | `read` | BOOL | Enable or disable entire group data recording. Can be modified in GUI. |
            | `sensor_list` | LIST | A string list of sensor IDs, configured in [`sensors` config section](#sensor-types). |
            """
        )
        ## Platform group
        group_platform_col_1, group_platform_col_2 = group_tab_platform.columns(2)
        group_platform_col_1.markdown(
            """
            #### Section example

            ```yaml
            name: Platform 1
            type: GROUP_PLATFORM
            read: true
            sensor_list:
            - p1_z1
            - p1_z2
            - p1_z3
            - p1_z4
            - p1_x1
            - p1_x2
            - p1_x3
            - p1_x4
            - p1_y1
            - p1_y2
            - p1_y3
            - p1_y4
            ```
            """
        )
        group_platform_col_1.warning(
            "Less sensors could be defined, with the specified key strings. In that case, **COP graphs** are not available.",
            icon=":material/warning:",
        )
        group_platform_col_1.error(
            "If sensor names does not include key strings, **total forces** and **COP graphs** are not available. The sensor group will be treated as a default one.",
            icon=":material/error:",
        )
        group_platform_col_2.markdown(
            """
            #### Group description

            Configure a platform with the `GROUP_PLATFORM` type. This group type only expects  `SENSOR_LOADCELL` type sensors, with a maximum of 12 (4 sensors on each axis).

            To obtain platform graphs such as **total forces** or **COP values**; sensors must have the following strings included in their names:
            - The 4 X-axis sensors: `_X_n`.
            - The 4 Y-axis sensors: `_Y_n`.
            - The 4 Z-axis sensors: `_Z_n`.

            Being $n = \{1, 2, 3, 4\}$ depending on the sensor location in the platform:
            """
        )
        group_platform_col_2.image(
            image="images/platform.png",
            caption="Platform sensor locations",
            use_column_width=True,
        )
        group_tab_platform.markdown(
            """
            Information of all the keys involved in this config section:

            | Key | Type | Description |
            | :--- | :---: | :--- |
            | `name` | STRING | Group name. |
            | `type` | STRING | Group type: `GROUP_DEFAULT` or `GROUP_PLATFORM`. |
            | `read` | BOOL | Enable or disable entire group data recording. Can be modified in GUI. |
            | `sensor_list` | LIST | A string list of sensor IDs, configured in [`sensors` config section](#sensor-types). |
            """
        )

    with st.expander("Configure your sensors", icon=":material/toggle_on:"):
        st.write(
            "You can modify general test and sensor settings of the configuration file on the settings page."
        )
        st.info(
            "When settings are modified, the changes are also saved in the configuration file.",
            icon=":material/info:",
        )
        st.subheader("General test settings")
        st.markdown(
            """
            Here you can still modify the recording settings of the configuration file.

            | Option | Minimum value | Maximum value | Description |
            | :--- | :---: | :---: | :--- |
            | Recording interval | `10` | `1000` | Timeframe between each data recording in milliseconds. |
            | Tare amount | `10` | `500` | Amount of values to be taken for sensor new intercepts. |
            """
        )
        st.subheader("Sensor settings")
        st.markdown(
            """
            You can enable and disable sensors and sensor groups from the loaded configuration file, marking or unmarking the corresponding checkbox.

            - **Enable a sensor**: The app will attempt to connect to this sensor, at the specified `serial` (and `channel` if needed) in the configuration file.
            - **Disable a sensor**: The sensor will be ignored. This means the app will not attempt a connection with the sensor.
            - **Enable a sensor group**: The app will try to connect only to enabled sensors. Disabled sensors inside an enabled sensor group are still ignored.
            - **Disable a sensor group**: The complete sensor list will be ignored, avoiding connection attempts even if there are enabled sensors.
            """
        )
        st.warning(
            "All sensors inside a disabled sensor group will be ignored.",
            icon=":material/warning:",
        )
        st.subheader("Sensor connection")
        st.markdown(
            """
            Click the `Connect sensors` button in order to check the enabled sensors connections.
            Once the connection check is done, the tab list below will update with the new sensor status.
            """
        )
        st.info(
            "To be able to preform tests, at least one sensor must be available.",
            icon=":material/info:",
        )

    st.header("Dashboard page")

    with st.expander("Run a test", icon=":material/play_arrow:"):
        st.write("Asd")

    with st.expander("Check and visualize the results", icon=":material/bar_chart:"):
        st.write("Asd")
