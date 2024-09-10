import streamlit as st
import plotly.graph_objects as go
import numpy as np


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
    st.plotly_chart(exampleFigure())

    figures_col_1, figures_col_2 = st.columns(2)
    figures_col_1.multiselect(
        label="Select individual sensors",
        options=["A","B","C"],
        placeholder="Choose one or more sensors",
        help="Plot one or more individual sensor data on the same plot."
    )
    figures_col_2.selectbox(
        label="Select platform",
        options=["Platform A","Platform B"],
        index=None,
        placeholder="Choose a platform",
        help="Plot platform results."
    )

    with st.expander("**Data settings**", icon=":material/dataset:"):
        settings_col_1, settings_col_2 = st.columns(2)
        settings_col_1.subheader("Recorded data")
        settings_col_1.radio(
            label="Data type",
            options=[
                "Raw",
                "Calibrated"
            ],
            captions=[
                "Just as recorded",
                "Calibrated param"
            ],
            horizontal=True
        )
        settings_col_1.radio(
            label="Figure type",
            options=[
                "Sensor",
                "Platform"
            ],
            captions=[
                "Individual sensors",
                "A force platform"
            ],
            horizontal=True
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
            max_value=100, # TODO the fs max value
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
        
