import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd
import threading
import time

from streamlit.runtime.scriptrunner import get_script_run_ctx, add_script_run_ctx

from loguru import logger


stop_event = threading.Event()


def readTest(detain_event: threading.Event, session_id: str):
    ctx = get_script_run_ctx()
    if ctx.session_id != session_id:
        return
    assert "test_mngr" in st.session_state
    st.session_state.test_mngr.testStart("", "This is a test")
    test_itr = 0
    while not detain_event.is_set():
        ctx = get_script_run_ctx()
        if ctx.session_id != session_id:
            break
        st.session_state.test_mngr.testRegisterValues()
        test_itr += 1
        if test_itr > 1000:
            st.session_state.test_reading = False
            break
        time.sleep(0.01)
    st.session_state.test_mngr.testStop("This is a test")


def getSensorDataFrame() -> pd.DataFrame:
    df = pd.DataFrame({"timestamp": [0], "sensor_data": [0]})
    if not "sensor_mngr" in st.session_state or not "test_mngr" in st.session_state:
        return df
    sensor_group = st.session_state.sensor_mngr.getGroup("imus")
    if sensor_group is None:
        return df
    sensor_dict = sensor_group.getSensors(only_available=True)
    if not sensor_dict:
        return df
    sensor = sensor_dict["imu_1"]
    if sensor is None:
        return df
    sensor_data = sensor.getValues()
    times = st.session_state.test_mngr.getTestTimes()
    if not sensor_data or len(sensor_data) != len(times):
        return pd.DataFrame({"timestamp": [0], "sensor_data": [0]})
    df = pd.DataFrame({"timestamp": times, "sensor_data": sensor_data})
    return df


def exampleFigure() -> go.Figure:
    x = np.linspace(0, 10, 100)
    y = np.sin(x)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Seno"))

    fig.update_layout(
        title="Gráfico de ejemplo con Plotly", xaxis_title="X", yaxis_title="Y"
    )

    return fig


def dashboardPage():
    # Init variables
    if "test_reading" not in st.session_state:
        st.session_state.test_reading = False

    # Load page
    st.subheader("Control panel")

    test_unavailable = True
    if (
        "test_mngr" in st.session_state
        and st.session_state.test_mngr.getSensorConnected()
    ):
        test_unavailable = False
    if test_unavailable:
        st.warning(
            "Need to connect sensors! Go to the settings page.",
            icon=":material/offline_bolt:",
        )

    if st.session_state.get("btn_test_start", False):
        st.session_state.test_reading = True
    elif st.session_state.get("btn_test_stop", False):
        st.session_state.test_reading = False

    panel_col_1, panel_col_2, panel_col_3 = st.columns(3)
    btn_test_start = panel_col_1.button(
        label="Start test",
        key="btn_test_start",
        type="primary",
        use_container_width=True,
        disabled=test_unavailable or st.session_state.test_reading,
    )
    btn_test_stop = panel_col_2.button(
        label="Stop test",
        key="btn_test_stop",
        type="primary",
        use_container_width=True,
        disabled=test_unavailable or not st.session_state.test_reading,
    )
    btn_test_tare = panel_col_3.button(
        label="Tare sensors",
        key="btn_test_tare",
        type="secondary",
        use_container_width=True,
        disabled=test_unavailable or not st.session_state.test_reading,
    )

    if st.session_state.test_reading:
        st.info(
            "A current test is running! Click on **Stop test** when finished.",
            icon=":material/play_circle:",
        )

    if btn_test_start:
        stop_event.clear()
        ctx = get_script_run_ctx()
        thread = threading.Thread(target=readTest, args=(stop_event, ctx.session_id))
        add_script_run_ctx(thread)
        thread.start()
    if btn_test_stop:
        stop_event.set()

    st.dataframe(data=getSensorDataFrame(), use_container_width=True)

    st.subheader("Graph results")

    with st.expander("**Data settings**", icon=":material/dataset:"):
        settings_col_1, settings_col_2 = st.columns(2)
        settings_col_1.subheader("Recorded data")
        data_type = settings_col_1.radio(
            label="Data type",
            options=["Raw", "Calibrated"],
            captions=["Just as recorded", "Calibrated param"],
            horizontal=True,
        )
        figure_type = settings_col_1.radio(
            label="Figure type",
            options=["Sensor", "Platform"],
            captions=["Individual sensors", "A force platform"],
            horizontal=True,
        )
        if figure_type == "Sensor":
            settings_col_1.multiselect(
                label="Select individual sensors",
                options=["A", "B", "C"],
                placeholder="Choose one or more sensors",
                help="Plot one or more individual sensor data on the same plot.",
            )
        else:
            settings_col_1.selectbox(
                label="Select platform",
                options=["Platform A", "Platform B"],
                index=None,
                placeholder="Choose a platform",
                help="Plot platform results.",
            )
        settings_col_2.subheader("Butterworth filter")
        # TODO this setting needs to be related to reading frequency: f = 1/t
        settings_col_2.number_input(
            label="Sampling rate (Hz)",
            key="number_input_butter_fs",
            min_value=10,
            max_value=500,
            value=100,
            disabled=True,
            help="TODO",
        )
        settings_col_2.number_input(
            label="Cutoff frequency (Hz)",
            key="number_input_butter_fc",
            min_value=1,
            max_value=100,  # TODO the fs max value
            value=10,
            help="TODO",
        )
        settings_col_2.number_input(
            label="Filter order",
            key="number_input_butter_order",
            min_value=2,
            max_value=6,
            value=6,
            help="TODO",
        )

    # TODO Generate different figures depending on settings
    st.plotly_chart(exampleFigure())
