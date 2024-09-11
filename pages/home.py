import streamlit as st


def homePage():
    _, img_col, _ = st.columns([0.2, 0.6, 0.2])
    img_col.image(
        image="images/home_project_logo.png",
        use_column_width=True,
    )
    st.title("Welcome to Force Platform Reader")
    st.write(
        "Check the following documentation if you are not familiar with the application."
    )

    with st.expander("**Load a custom config file**", icon=":material/upload_file:"):
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
        st.info(
            "There are some requirements for certain sensor types and platform sensor groups.\nCheck the following information.",
            icon=":material/info:",
        )
        st.subheader("Sensor types")
        sensor_col_1, sensor_col_2, sensor_col_3 = st.columns(3)
        code_sensor_loadcell = """
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
            """
        code_sensor_imu = """
            name: IMU_Leg_Right
            type: SENSOR_IMU
            read: true
            connection:
              serial: /dev/serial/by-path/pci-0000:00:14.0-usb-0:1.1.4.3:1.0-port0
            properties:
              tag: IMU_1
            """
        code_sensor_encoder = """
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
            """
        sensor_col_1.markdown("Type `SENSOR_LOADCELL`")
        sensor_col_2.markdown("Type `SENSOR_IMU`")
        sensor_col_3.markdown("Type `SENSOR_ENCODER`")
        sensor_col_1.code(code_sensor_loadcell, language="yaml")
        sensor_col_2.code(code_sensor_imu, language="yaml")
        sensor_col_3.code(code_sensor_encoder, language="yaml")

        st.subheader("Sensor group types")
        sensor_group_col_1, sensor_group_col_2 = st.columns(2)
        code_sensor_group_default = """
            name: Body IMUs
            type: GROUP_DEFAULT
            read: true
            sensor_list:
            - imu_1
            - imu_2
            - imu_3
            """
        code_sensor_group_platform = """
            name: Platform 1
            type: GROUP_PLATFORM
            read: true
            sensor_list:
            - p1_z1
            - p1_z2
            - p1_z3
            """
        sensor_group_col_1.markdown("Type `GROUP_DEFAULT`")
        sensor_group_col_2.markdown("Type `GROUP_PLATFORM`")
        sensor_group_col_1.code(code_sensor_group_default, language="yaml")
        sensor_group_col_2.code(code_sensor_group_platform, language="yaml")

    with st.expander("Configure your sensors", icon=":material/toggle_on:"):
        st.write(
            "You can enable and disable sensors and sensor groups from the loaded config file."
        )

    with st.expander("Calibrate your sensors", icon=":material/eye_tracking:"):
        st.write("You can calibrate individual sensors and force platorms.")

        st.subheader("Individual sensors")
        st.markdown("Available sensor types: `SENSOR_LOADCELL`")
        st.latex(
            r"""
            F = k ~ V_f
            """
        )

        st.subheader("Force platform sensor groups")
        st.warning(
            "Only available for project custom platforms.", icon=":material/warning:"
        )
        st.latex(
            r"""
            \begin{bmatrix}
                \mathbf{Z_f^1}\\
                \mathbf{Z_f^2}\\
                \vdots\\
                \mathbf{Z_f^{M-1}}\\
                \mathbf{Z_f^M}\\
            \end{bmatrix}
            \begin{bmatrix}
                k_{1,1} \\
                k_{1,2} \\
                \vdots \\
                k_{1,12} \\
                k_{2,1} \\
                \vdots \\
                k_{6,12}
            \end{bmatrix} =
            \begin{bmatrix}
                \mathbf{f^1}\\
                \mathbf{f^2}\\
                \vdots\\
                \mathbf{f^{M-1}}\\
                \mathbf{f^{M}}
            \end{bmatrix}
            """
        )
        st.latex(
            r"""
            \mathbf{Z_f} = \mathbf{I_6} \otimes \mathbf{v_f}^T
            """
        )
        ec_col_1, ec_col_2 = st.columns(2)
        ec_col_1.latex(
            r"""
            \mathbf{v_f} = \{V_{f1}, V_{f2}, \dots, V_{f12}\}^T
            """
        )
        ec_col_2.latex(
            r"""
            \mathbf{f} = \{F_x, F_y, F_z, M_x, M_y, M_z\}^T
            """
        )

    with st.expander("Run a test", icon=":material/play_arrow:"):
        st.write("Asd")

    with st.expander("Check and visualize the results", icon=":material/bar_chart:"):
        st.write("Asd")
