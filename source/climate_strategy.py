import streamlit as st
import pandas as pd
from enum import Enum
from plots import show_area_plot, line_chart, test
from metadata import action_areas as aa
import json
import os

from sim import m1, m2, m3
from utils import convert_df

# constants
DATA_PATH = "./source/data/"
INDICATORS_METADATA = os.path.join(DATA_PATH, "goal_indicators.csv")
REFERENCES = os.path.join(DATA_PATH, "references.csv")
PLOTS = os.path.join(DATA_PATH, "plots.csv")
TIME_SERIES = os.path.join(DATA_PATH, "time_series.csv")
TIME_SERIES_GOALS = os.path.join(DATA_PATH, "time_series_goal.csv")
DATASETS = os.path.join(DATA_PATH, "dataset.csv")
SCENARIOS_FILE = os.path.join(DATA_PATH, "scenario.csv")

SIM_DICT = {'M1': m1.CarSimulation, 'M2': m2.TruckSimulation}


class DatasetTypes(Enum):
    base = 1
    goal = 2
    scenario_low = 3
    scenario_medium = 4
    scenario_high = 5


class ActionAreaTypes(Enum):
    MOBILITY = "AA1"
    BUILDINGS = "AA2"
    CONSTRUCTION = "AA3"
    ECONOMY = "AA4"
    ENERGY_SUPPLY = "AA5"
    WASTE_DISPOSAL_CSS = "AA6"
    AGRICULTURE_FOREST = "AA7"


class Goal:
    def __init__(self, description, title):
        self.description = description
        self.title = title


def show_references():
    df = pd.read_csv(REFERENCES, sep=";")
    st.markdown("## Referenzen")
    for index, row in df.iterrows():
        st.markdown(f'- [{row["text"]}]({row["url"]}): {row["description"]}')


def show_scenarios():
    st.markdown("## Szenarien")
    scenario_list = []
    for key, action_area in action_areas.items():
        for key, goal in action_area["goals"].items():
            if "scenarios" in goal:
                for key, scenario in goal["scenarios"].items():
                    st.write(key)
                    st.write(scenario)


def get_dic_datasets() -> dict:
    """
    Reads a CSV file and returns a dictionary with the dataset names as keys and their corresponding IDs as values.

    Returns:
        dict: A dictionary mapping dataset names to their IDs.
    """
    df = pd.read_csv(DATASETS, sep=";")
    return dict(zip(df["name"], df["id"]))


def show_data():
    st.markdown("## Zeitreihen")


DIC_DATASETS = get_dic_datasets()


class ActionArea:
    def __init__(self, id: ActionAreaTypes):
        self.id = id
        self.description = aa[id]["description"]
        self.title = aa[id]["title"]
        self.menu_text = aa[id]["menu_text"]
        self.menu_icon = aa[id]["menu_icon"]
        self.goals = aa[id]["goals"]
        self.measures = []
        self.time_series_options = []  # self.get_time_series_options(id)
        self.hist_values = []  # self.get_hist_data(id)
        self.plots = []  # self.get_plots(id)
        self.plot_options = []  # list(self.plots['plot_name'].unique())
        self._current_goal = None
        self.current_simulation = None
    
    @property
    def current_goal(self):
        return self._current_goal
    
    @current_goal.setter
    def current_goal(self, value):
        self._current_goal = value
        if value in SIM_DICT:
            self.current_simulation = SIM_DICT[value](value)
        else:
            self.current_simulation = None

    def get_goal_datasets(self, goal: str, types: list) -> list:
        df = pd.read_csv(TIME_SERIES_GOALS, sep=";")
        df = df[(df["goal"] == goal) & (df["type"].isin(types))]
        dataset_list = df["ts_id"]
        return dataset_list

    def get_plots(self, aa_id: str):
        df = pd.read_csv(PLOTS, sep=";")
        df = df[df["action_area"] == aa_id]
        return df

    def get_time_series_options(self, id: str) -> list:
        df = pd.read_csv(INDICATORS_METADATA, sep=";")
        return list(df["kategorie"])

    def get_hist_data(self, aa_id: str):
        df = pd.read_csv(TIME_SERIES, sep=";")
        df = df[df["kategorie1"].isin(self.time_series_options)]
        return df

    def get_scenarios(self, aa_id: str):
        df = pd.read_csv(SCENARIOS_FILE, sep=";")
        df = df[df["kategorie"].isin(self.time_series_options)]
        return df

    def __repr__(self) -> str:
        return f"ActionArea({self.id}, {self.title})"

    def show_plot(self, plot: dict):
        df = self.hist_values[self.hist_values["kategorie1"] == plot["data_series"]]
        if plot["plot_type"] == "line":
            st.line_chart(df)
        if plot["plot_type"] == "bar":
            st.bar_chart(df)
        if plot["plot_type"] == "area":
            settings = json.loads(plot["plot_settings"])
            fig = show_area_plot(df, settings)
        st.plotly_chart(fig)

    def get_filter(self, df):
        filter = {}
        with st.sidebar.expander("🔍Filter"):
            filter["kategorie1"] = st.selectbox(
                "Kategorie 1", options=self.time_series_options
            )
            filter["kategorie2"] = st.selectbox(
                "Kategorie 2", options=self.time_series_options
            )
            filter["kategorie3"] = st.selectbox(
                "Kategorie 3", options=self.time_series_options
            )
        return df

    def get_value(self, key: str):
        return 2023, round(0.032904665 * 100, 1)

    def display_goal_indicator(self, indicator: dict, goal_key: str):
        st.markdown(f'{indicator["title"]}')
        st.markdown(f'{indicator["description"]}')
        
        if "target" in indicator:
            for key, value in indicator["target"].items():
                st.markdown(f"Ziel ({key}): {value}")
                year, value = self.get_value(key)
                st.markdown(f"Ist ({year}): {value}%")
        
        with st.expander("Daten & Grafik", expanded=True):
            plot, plot_df = self.current_simulation.get_plot()
            st.plotly_chart(plot)
            st.download_button(
                label="Daten herunterladen",
                data=plot_df.to_csv().encode('utf-8'),
                file_name='large_df.csv',
                mime='text/csv',
            )
                

        
    def show_ui(self):
        st.markdown(f"## {self.title}")
        tabs = st.tabs(["Info", "Ziele", "Basisdaten", "Bewertung"])
        with tabs[0]:
            st.markdown(self.description)
        with tabs[1]:
            self.current_goal = st.selectbox("Ziel", options=self.goals.keys())
            goal = self.goals[self.current_goal]
            st.markdown(f'**{self.current_goal}: {goal["title"]}**')
            st.markdown(goal["description"])
            if self.current_simulation is not None:
                st.markdown(f"---")
                st.markdown(
                    f'**Methodik:**\n\n{goal["monitoring"]}', unsafe_allow_html=True
                )
                st.markdown("**Szenarien**")
                with st.expander("Faktoren", expanded=True):
                    allow_edit = st.toggle("Bearbeiten", value=False)
                    df = self.current_simulation.intervals_df
                    edited_df = st.data_editor(df)
                    if allow_edit:
                        if st.button('Speichern'):
                            self.current_simulation.save_edits(edited_df)
                            st.success('Die Änderungen wurden erfolgreich gespeichert. Führe eine Neuberechnung durch, um die Auswirkungen in der Grafik sichtbar zu machen.')
                        if st.button("🧮Neu Berechnen"):
                            self.current_simulation.run()
                            self.current_simulation.save()
                with st.expander("Beschreibung der Szenarien"):
                    st.write(goal["scenarios"])
                st.markdown("---")
                st.markdown("***Ziel-Indikator(en):***")
                for key, goal in goal["goal-indicators"].items():
                    self.display_goal_indicator(goal, self.current_goal)
            else:
                st.warning("Dieses Ziel hat noch keine Simulation")

        with tabs[2]:
            if self.current_simulation:
                st.data_editor(self.current_simulation.data, hide_index=True)

        with tabs[3]:
            for key, goal in self.goals.items():
                st.markdown(f"#### {key}")
                st.markdown(f'Bewertung von *{goal["title"]}*')