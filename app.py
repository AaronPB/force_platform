import streamlit as st
import pandas as pd
from pages import home, settings, dashboard


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


if __name__ == "__main__":
    main()
