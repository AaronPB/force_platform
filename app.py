import streamlit as st
import pandas as pd
from pages import home, settings, dashboard, sensor_test


def dataframeExample() -> pd.DataFrame:
    data = {"test1": [0, 1, 2], "test2": [4, 5, 6]}
    return pd.DataFrame(data)


def main():
    # Page configuration
    st.set_page_config(
        page_title="Force Platform Reader",
        page_icon=":material/capture:",
        # layout="wide",
        initial_sidebar_state="expanded",
    )
    # Logo
    st.logo(
        image="images/project_logo.png",
        icon_image="images/project_icon.png",
        link="https://github.com/AaronPB",
    )
    # Load pages
    pg = st.navigation(
        [
            st.Page(
                home.homePage,
                title="Home",
                icon=":material/home:",
            ),
            st.Page(
                settings.settingsPage,
                title="Settings",
                icon=":material/settings:",
            ),
            st.Page(
                dashboard.dashboardPage,
                title="Dashboard",
                icon=":material/table_chart_view:",
            ),
        ]
    )
    pg.run()

    # Build sidebar
    # - Control panel
    st.sidebar.header("Control panel")

    test_col_1, test_col_2 = st.sidebar.columns(2)

    test_col_1.button(
        label="Start test",
        key="button_test_start",
        type="primary",
        use_container_width=True,
    )
    test_col_2.button(
        label="Stop test",
        key="button_test_stop",
        type="primary",
        use_container_width=True,
    )

    tare_button = st.sidebar.button(
        label="Tare sensors",
        key="button_tare_sensors",
        type="secondary",
        use_container_width=True,
    )

    # - Status information
    # st.sidebar.success("All ok to begin a test!", icon=":material/check_circle:")
    st.sidebar.warning("Need to connect sensors!", icon=":material/offline_bolt:")

    st.sidebar.divider()

    # - Download buttons
    download_col_1, download_col_2 = st.sidebar.columns(2)

    download_file = download_col_1.download_button(
        label="Download raw",
        key="download_button_data_raw",
        type="secondary",
        use_container_width=True,
        file_name="test.csv",
        help="Download csv file with recorded data",
        disabled=True,
        data=dataframeExample().to_csv(index=False).encode("utf-8"),
    )
    download_file2 = download_col_2.download_button(
        label="Download calibrated",
        key="download_button_data_calibrated",
        type="secondary",
        use_container_width=True,
        file_name="test.csv",
        help="Download csv file with recorded data",
        disabled=True,
        data=dataframeExample().to_csv(index=False).encode("utf-8"),
    )

    # Credits
    st.sidebar.empty()
    st.sidebar.write("AaronPB")


if __name__ == "__main__":
    main()
