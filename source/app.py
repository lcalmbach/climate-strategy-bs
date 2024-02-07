import streamlit as st
from streamlit_option_menu import option_menu
from datasets import DataBrowser

from climate_strategy import (
    ActionAreaTypes,
    ActionArea,
    show_references,
    show_data,
    show_scenarios,
)
from dashboard import Dashboard

__version__ = "0.0.5"
__author__ = "Statistisches Amt des Kantons Basel-Stadt"
__author_email__ = "stata@bs.ch"
VERSION_DATE = "2024-02-06"
GIT_REPO = "https://github.com/lcalmbach/climate-strategy-bs"
MY_EMOJI = "🔮"
MY_NAME = "KSS-Monitoring"


def init():
    st.set_page_config(
    page_title=MY_NAME,
    page_icon=MY_EMOJI,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)
def get_menu():
    menu_items = []
    menu_icons = []
    for key, value in st.session_state["action-areas"].items():
        menu_items.append(value.menu_text)
        menu_icons.append(value.menu_icon)

    menu_items.append("---")
    menu_icons.append("")
    menu_items.append("Daten")
    menu_icons.append("database")
    menu_items.append("Dashboard")
    menu_icons.append("speedometer")
    menu_items.append("Referenzen")
    menu_icons.append("box-arrow-up-right")
    return menu_items, menu_icons


def show_info_box():
    """
    Displays an information box in the sidebar with author information, version number, and a link to the git repository.

    Parameters:
    None

    Returns:
    None
    """
    impressum = f"""<div style="background-color:#34282C; padding: 10px;border-radius: 15px; border:solid 1px white;">
    <small>Autor: <a href="mailto:{__author_email__}">{__author__}</a><br>
    🚧 Version: {__version__} ({VERSION_DATE})<br>
    <a href="{GIT_REPO}" style="color:white">Git-Repository</a></small>
    """
    st.sidebar.markdown(impressum, unsafe_allow_html=True)


def main():
    init()
    if not ("action-areas" in st.session_state):
        st.session_state["action-areas"] = {}
        for x in [member.value for member in ActionAreaTypes]:
            st.session_state["action-areas"][x] = ActionArea(x)
        st.session_state['dashboard'] = Dashboard()

    menu_items, menu_icons = get_menu()
    with st.sidebar:
        selected = option_menu(
            MY_NAME,
            menu_items,
            icons=menu_icons,
            menu_icon="globe",
            default_index=0,
        )
    if selected == "Referenzen":
        show_references()
    elif selected == "Daten":
        app = DataBrowser()
        app.show_ui()
    elif selected == "Dashboard":
        st.session_state['dashboard'].show_ui()
    else:
        action_area = [
            obj
            for obj in st.session_state["action-areas"].values()
            if obj.menu_text == selected
        ][0]
        action_area.show_ui()
    show_info_box()


if __name__ == "__main__":
    main()
