import streamlit as st
import pandas as pd


def settings_page():
    st.file_uploader(
        label="Load a custom config file",
        type=".yaml",
        accept_multiple_files=False,
        help="The app will update all sensors and general settings with the new custom configuration.",
    )

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
        value=300,
        help="TODO",
    )
    test_col_2.number_input(
        label="Record frequency (ms)",
        key="number_input_record_freq",
        min_value=10,
        max_value=1000,
        value=10,
        help="TODO",
    )
    test_col_2.number_input(
        label="Calibration amount",
        key="number_input_calibration_amount",
        min_value=10,
        max_value=500,
        value=300,
        help="TODO",
    )

    # Sensor settings
    st.header("Sensor settings")

    connect_col_1, connect_col_2 = st.columns(2)
    connect_col_1.button(label="Connect sensors", type="primary")

    st.error("There is no sensor group information available!")

    # This will be loaded once sensors are connected

    st.write("This will be loaded when parsing sensors from config")

    df = pd.DataFrame(
        [
            {"Name": "Loadcell_1", "Connect": True, "Type": "LOADCELL", "Status": "NOT CONNECTED"},
            {"Name": "Loadcell_2", "Connect": False, "Type": "LOADCELL", "Status": "NOT CONNECTED"},
            {"Name": "Loadcell_3", "Connect": True, "Type": "LOADCELL", "Status": "NOT CONNECTED"},
        ]
    )
    no_tab, tab2 = st.tabs(["Sensor group", "Example"])
    with no_tab:
        st.error("There is no sensor group information available!")
    with tab2:
        st.checkbox(
            label="Disable entire sensor group",
            value=False,
            help="Ignores and does not connect to enabled sensors of this group."
        )
        edited_df = st.data_editor(
            data=df,
            use_container_width=True,
            hide_index=True,
            disabled=("Name", "Type", "Status")
        )
