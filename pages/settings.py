import streamlit as st
import pandas as pd

from src.managers.configManager import ConfigManager
from src.managers.sensorManager import SensorManager
from src.managers.fileManager import FileManager
from src.managers.testManager import TestManager

from src.enums.configPaths import ConfigPaths
from src.enums.sensorStatus import SStatus

from loguru import logger


def colorDataFrameRow(status: SStatus, columns: int):
    if status == SStatus.AVAILABLE:
        return ["background-color: #107523"] * columns
    elif status == SStatus.NOT_FOUND:
        return ["background-color: #8c0d0d"] * columns
    else:
        return ["background-color: transparent"] * columns


def connectSensors():
    st.session_state.sensor_connection_available = False
    st.session_state.test_mngr.setSensorGroups(st.session_state.sensor_mngr.getGroups())
    with st.spinner("Connecting sensors..."):
        st.session_state.test_mngr.checkConnection()
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

    st.file_uploader(
        label="Load a custom config file",
        type=".yaml",
        accept_multiple_files=False,
        help="The app will update all sensors and general settings with the new custom configuration.",
    )
    st.write(f"Loaded config: {st.session_state.config_mngr.getCurrentFilePath()}")

    # Test settings
    st.header("Test settings")
    test_col_1, test_col_2 = st.columns(2)
    test_col_1.text_input(
        label="Test name",
        placeholder="New test",
        help="Will be used for the data file name.",
    )
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
    test_col_2.number_input(
        label="Calibration amount",
        key="number_input_calibration_amount",
        min_value=10,
        max_value=500,
        value=st.session_state.config_mngr.getConfigValue(
            ConfigPaths.CALIBRATION_DATA_AMOUNT.value, 300
        ),
        help="TODO",
    )

    # Sensor settings
    st.header("Sensor settings")

    # FIXME Does not work because the button runs the method before updating/rendering the page.
    # if st.session_state.get("btn_sensor_connect", False):
    #     st.session_state.sensor_connection_available = False

    connect_col_1, connect_col_2 = st.columns(2)
    connect_col_1.button(
        label="Connect sensors",
        key="btn_sensor_connect",
        type="primary",
        on_click=connectSensors,
        disabled=not st.session_state.sensor_connection_available,
    )
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
        pass
    else:
        tab_names = []
        sensor_info = {}
        for group in sensor_groups:
            tab_names.append(group.getName())
            sensor_info[group.getName()] = {
                "names": [sensor.getName() for sensor in group.getSensors().values()],
                "types": [sensor.getType() for sensor in group.getSensors().values()],
                "read": [sensor.getRead() for sensor in group.getSensors().values()],
                "status": [
                    sensor.getStatus() for sensor in group.getSensors().values()
                ],
            }
        tabs = st.tabs(tab_names)
        for i, tab_name in enumerate(tab_names):
            df = pd.DataFrame(
                {
                    "Connect": sensor_info[tab_name]["read"],
                    "Name": sensor_info[tab_name]["names"],
                    "Type": sensor_info[tab_name]["types"],
                    "Status": sensor_info[tab_name]["status"],
                }
            )
            styled_df = df.style.apply(
                lambda x: colorDataFrameRow(x["Status"], len(df.columns)), axis=1
            )
            with tabs[i]:
                st.checkbox(
                    label="Disable entire sensor group",
                    key=f"checkbox_{i}",
                    value=False,
                    help="Ignores and does not connect to enabled sensors of this group.",
                )
                edited_df = st.data_editor(
                    data=styled_df,
                    key=f"edited_df_{i}",
                    use_container_width=True,
                    hide_index=True,
                    disabled=("Name", "Type", "Status"),
                )
