import streamlit as st
from streamlit_option_menu import option_menu
from climate_strategy import ActionAreaTypes, ActionArea, show_references, show_data, show_scenarios    


def get_menu():
    menu_items = []
    menu_icons = []
    for key, value in st.session_state['action-areas'].items():
        menu_items.append(value.menu_text)
        menu_icons.append(value.menu_icon)
    
    menu_items.append('Daten')
    menu_icons.append('database')
    menu_items.append('Szenarios')
    menu_icons.append('bar-chart-line')
    menu_items.append('Referenzen')
    menu_icons.append('box-arrow-up-right')
    return menu_items, menu_icons


def main():
    if not ('action-areas' in st.session_state):
        st.session_state['action-areas'] = {}
        for x in [member.value for member in ActionAreaTypes]:
            st.session_state['action-areas'][x] = ActionArea(x)

    menu_items, menu_icons = get_menu()
    with st.sidebar:
        selected = option_menu(
            "KSS Monitoring",
            menu_items,
            icons=menu_icons,
            menu_icon="globe",
            default_index=0)
    if selected == 'Referenzen':
        show_references()
    elif selected == 'Daten':
        show_data()
    elif selected == 'Szenarios':
        show_scenarios()
    else:
        action_area = [obj for obj in st.session_state['action-areas'].values() if obj.menu_text == selected][0]
        action_area.show_ui()


if __name__ == "__main__":
    main()