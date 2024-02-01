import streamlit as st
import pandas as pd
from enum import Enum
from plots import show_area_plot, line_chart
from data import action_areas
import json

from sim.m1 import CarSimulation

# constants
INDICATORS_METADATA = "./source/data/goal_indicators.csv"
REFERENCES = "./source/data/references.csv"
PLOTS = "./source/data/plots.csv"
TIME_SERIES = "./source/data/time_series.csv"
TIME_SERIES_GOALS = "./source/data/time_series_goal.csv"
DATASETS = "./source/data/dataset.csv"
SCENARIOS_FILE = "./source/data/scenario.csv"


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
        st.markdown(f"- [{row['text']}]({row['url']}): {row['description']}")


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
        self.description = action_areas[id]["description"]
        self.title = action_areas[id]["title"]
        self.menu_text = action_areas[id]["menu_text"]
        self.menu_icon = action_areas[id]["menu_icon"]
        self.goals = action_areas[id]["goals"]
        self.measures = []
        self.time_series_options = []  # self.get_time_series_options(id)
        self.hist_values = []  # self.get_hist_data(id)
        self.plots = []  # self.get_plots(id)
        self.plot_options = []  # list(self.plots['plot_name'].unique())

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

    def show_settings(self, plot: dict):
        with st.sidebar.expander("⚙️Einstellungen"):
            par1 = st.slider("Parameter 1", min_value=0, max_value=100, value=50)
            par2 = st.slider("Parameter 2", min_value=0, max_value=100, value=50)
            par3 = st.radio("Parameter 3", options=["Option 1", "Option 2", "Option 3"])

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
        return 2020, 10.4

    def display_goal_indicator(self, indicator: dict, goal_key: str):
        st.markdown(f"{indicator['title']}")
        st.markdown(f"{indicator['description']}")
        if "target" in indicator:
            for key, value in indicator["target"].items():
                st.markdown(f"Ziel ({key}): {value}")
                year, value = self.get_value(key)
                st.markdown(f"Ist ({year}): {value}")
        if st.button('🚀Neu Berechnen'):
            sim = CarSimulation()
            sim.run()
            fig = sim.plot()
            st.pyplot(fig=fig)
            sim.save()
        with st.expander("Daten & Grafik"):
            df = pd.read_csv(TIME_SERIES, sep=";")
            datasets = self.get_goal_datasets(
                goal_key,
                [
                    DatasetTypes.goal.value,
                    DatasetTypes.scenario_low.value,
                    DatasetTypes.scenario_medium.value,
                    DatasetTypes.scenario_high.value,
                ],
            )
            df = df[df["ts_id"].isin(datasets)]
            df_names = pd.read_csv(DATASETS, sep=";")
            # df_names['id'] = df_names['id'].astype(int)
            df["ts_id"] = df["ts_id"].astype(int)
            df = df.merge(df_names[["id", "name"]], left_on="ts_id", right_on="id")
            df = df[["ts_id", "jahr", "name", "wert"]]
            plot_settings = {
                "x": "jahr",
                "y": "wert",
                "color": "name",
                "color_name": "Szenario",
                "x_axis_title": "Jahr",
                "y_axis_title": 'Anteil emissionslos Fzg MIV %',
                "h_line": 97,
            }
            fig = line_chart(df, plot_settings)
            st.plotly_chart(fig)

    def show_ui(self):
        tabs = st.tabs(["Info", "Ziele", "Daten", "Grafiken", "Bewertung"])
        with tabs[0]:
            st.markdown(f"## {self.title}")
            st.markdown(self.description)
        with tabs[1]:
            sel_goal = st.selectbox("Ziel", options=self.goals.keys())
            goal = self.goals[sel_goal]
            st.markdown(f'**{sel_goal}: {goal["title"]}**')
            st.markdown(goal["description"])
            if "monitoring" in goal:
                st.markdown(f"---")
                st.markdown(
                    f'**Methodik:**\n\n{goal["monitoring"]}', unsafe_allow_html=True
                )
                with st.expander("Faktoren"):
                    allow_edit = st.toggle("Bearbeiten", value=False)
                    df = pd.read_csv(SCENARIOS_FILE, sep=";")
                    df = df[df["goal"] == sel_goal]
                    factors = list(df["factor"].unique())
                    sel_factor = st.selectbox("Faktor", options=factors)
                    df = df[df["factor"] == sel_factor]
                    st.data_editor(df)
                    if allow_edit:
                        if st.button("Speichern"):
                            st.success("Die Änderungen wurden erfolgreich gespeichert")
            if "goal-indicators" in goal:
                st.markdown("---")
                st.markdown("***Ziel-Indikator(en):***")
                for key, goal in goal["goal-indicators"].items():
                    self.display_goal_indicator(goal, sel_goal)
            if "time-series" in goal:
                st.markdown("**Auswertungen für die Berechnung der Ziel-Indikatoren**")
                for t2 in goal["time-series"]:
                    st.markdown(f"- {t2}")

        with tabs[2]:
            ...
            # sel_dataset = st.selectbox('Datensatz', options=self.time_series_options)
            # df = self.hist_values[self.hist_values['kategorie1'] == sel_dataset]
            # df = self.get_filter(df)
            # st.dataframe(df)
        with tabs[3]:
            if len(self.plot_options) > 0:
                sel_plot = st.selectbox("Graphik", options=self.plot_options)
                plot = self.plots[self.plots["plot_name"] == sel_plot].iloc[0]
                self.show_settings(plot)
                self.show_plot(plot)
            else:
                st.info("Keine Graphiken vorhanden")
        with tabs[4]:
            for key, goal in self.goals.items():
                st.markdown(f"#### {key}")
                st.markdown(f'Bewertung von *{goal["title"]}*')
