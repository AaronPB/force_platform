import streamlit as st
import pandas as pd

from src.managers.configManager import ConfigManager
from src.managers.sensorManager import SensorManager
from src.managers.fileManager import FileManager
from src.managers.testManager import TestManager

from src.enums.configPaths import ConfigPaths

from loguru import logger


def connectSensors():
    st.session_state.sensor_connection_available = False
    with st.spinner("Connecting sensors..."):
        st.session_state.test_mngr.checkConnection(
            st.session_state.sensor_mngr.getGroups()
        )
    st.session_state.sensor_connection_available = True


def newConfigFile(file_path: str):
    st.session_state.sensor_mngr = SensorManager()
    st.session_state.file_mngr = FileManager()

    st.session_state.config_mngr.loadConfigFile(file_path)
    st.session_state.sensor_mngr.setup(st.session_state.config_mngr)
    if "file_mngr" in st.session_state:
        st.session_state.file_mngr.setup(st.session_state.config_mngr)


def settingsPage():
    # Initialize global instances
    if "config_mngr" not in st.session_state:
        logger.info("Defining config manager")
        st.session_state.config_mngr = ConfigManager()
    if "sensor_mngr" not in st.session_state:
        st.session_state.sensor_mngr = SensorManager()
        st.session_state.sensor_mngr.setup(st.session_state.config_mngr)
    if "test_mngr" not in st.session_state:
        st.session_state.test_mngr = TestManager()

    # Buttons
    if "sensor_connection_available" not in st.session_state:
        # TODO Maybe False if there are errors with config loads?
        st.session_state.sensor_connection_available = True

    st.text_input(
        label="Loaded configuration file name",
        value=st.session_state.config_mngr.getConfigValue(
            ConfigPaths.CONFIG_NAME.value, "Default file"
        ),
        disabled=True,
    )

    file_upload = st.file_uploader(
        label="Load a custom configuration file",
        type=".yaml",
        accept_multiple_files=False,
        help="The app will update all sensors and general settings with the new custom configuration.",
    )
    if file_upload is not None:
        st.session_state.config_mngr.updateCustomConfig(file_upload)
        st.session_state.sensor_mngr.setup(st.session_state.config_mngr)
        st.rerun()

    # Test settings
    st.header("Test settings")
    test_col_1, test_col_2 = st.columns(2)
    test_col_1.number_input(
        label="Tare amount",
        key="number_input_tare_amount",
        min_value=10,
        max_value=500,
        value=st.session_state.config_mngr.getConfigValue(
            ConfigPaths.RECORD_TARE_AMOUNT.value, 300
        ),
        help="TODO",
    )
    test_col_2.number_input(
        label="Record frequency (ms)",
        key="number_input_record_freq",
        min_value=10,
        max_value=1000,
        value=st.session_state.config_mngr.getConfigValue(
            ConfigPaths.RECORD_INTERVAL_MS.value, 10
        ),
        help="TODO",
    )

    # Sensor settings
    st.header("Sensor settings")

    if st.session_state.get("btn_sensor_connect", False):
        st.session_state.sensor_connection_available = False

    connect_col_1, connect_col_2 = st.columns(2)
    connect_sensors_btn = connect_col_1.button(
        label="Connect sensors",
        key="btn_sensor_connect",
        type="primary",
        disabled=not st.session_state.sensor_connection_available,
    )
    if connect_sensors_btn:
        connectSensors()
        st.rerun()
    if st.session_state.test_mngr.getSensorConnected():
        connect_col_2.success("Sensors connected!", icon=":material/check_circle:")
    else:
        connect_col_2.warning(
            "Need to connect sensors!", icon=":material/offline_bolt:"
        )

    sensor_groups = st.session_state.sensor_mngr.getGroups()
    if not sensor_groups:
        st.error("There is no sensor group information available!")
    elif len(sensor_groups) == 1:
        # TODO Build single window instead of tabs
        return

    tab_names = [group.getName() for group in sensor_groups]
    tabs = st.tabs(tab_names)
    for i, group in enumerate(sensor_groups):
        df = pd.DataFrame(
            {
                "ID": [sensor.getID() for sensor in group.getSensors().values()],
                "Connect": [sensor.getRead() for sensor in group.getSensors().values()],
                "Name": [sensor.getName() for sensor in group.getSensors().values()],
                "Type": [
                    sensor.getType().value for sensor in group.getSensors().values()
                ],
                "Status": [
                    sensor.getStatus().value for sensor in group.getSensors().values()
                ],
            }
        )
        with tabs[i]:
            disable_group = st.checkbox(
                label="Disable entire sensor group",
                key=f"checkbox_{i}",
                value=not group.getRead(),
                help="Ignores and does not connect to enabled sensors of this group.",
            )
            if disable_group:
                st.session_state.sensor_mngr.setSensorRead(
                    not group.getRead(), group.getID()
                )
                st.rerun()
            edited_df = st.data_editor(
                data=df,
                key=f"edited_df_{i}",
                use_container_width=True,
                hide_index=True,
                column_order=("Connect", "Name", "Type", "Status"),
                disabled=("Name", "Type", "Status"),
            )
            changed_sensors = df[df["Connect"] != edited_df["Connect"]]
            if not changed_sensors.empty:
                for index, row in changed_sensors.iterrows():
                    st.session_state.sensor_mngr.setSensorRead(
                        not row["Connect"], group.getID(), row["ID"]
                    )
                st.rerun()
