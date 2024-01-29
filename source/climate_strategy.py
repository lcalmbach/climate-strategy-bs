import streamlit as st
import pandas as pd
from enum import Enum
from data import data
from plots import show_area_plot
import json

# constants
INDICATORS_METADATA = './data/goal_indicators.csv'
REFERENCES = './data/references.csv'
PLOTS = './data/plots.csv'
HISTORIC_VALUES = './data/time_series.csv'
PREDICTION_VALIUES = './data/prediction_values.csv'
SCENARIOS_FILE = './data/scenario.csv'


class ActionAreaTypes(Enum):
    MOBILITY = 'AA1'
    BUILDINGS = 'AA2'
    CONSTRUCTION = 'AA3'
    ECONOMY = 'AA4'
    ENERGY_SUPPLY ='AA5'
    WASTE_DISPOSAL_CSS = 'AA6'
    AGRICULTURE_FOREST = 'AA7'


class Goal:
    def __init__(self, description, title):
        self.description = description
        self.title = title


def show_references():
    df = pd.read_csv(REFERENCES, sep=';')
    st.markdown('## Referenzen')
    for index, row in df.iterrows():
        st.markdown(f"- [{row['text']}]({row['url']}): {row['description']}")


def show_scenarios():
    st.markdown('## Szenarien')


def show_data():
    st.markdown('## Zeitreihen')


class ActionArea:
    def __init__(self, id: ActionAreaTypes):
        self.id = id
        self.description = data[id]['description']
        self.title = data[id]['title']
        self.menu_text = data[id]['menu_text']
        self.menu_icon = data[id]['menu_icon']
        self.goals = data[id]['goals']
        self.measures = []
        self.time_series_options = [] #self.get_time_series_options(id)
        self.hist_values = [] # self.get_hist_data(id)
        self.plots = [] # self.get_plots(id)
        self.plot_options = [] # list(self.plots['plot_name'].unique())
        self.predictions = [] # self.get_prediction_data(id)

    def get_plots(self, aa_id: str):
        df = pd.read_csv(PLOTS, sep=';')
        df = df[df['action_area'] == aa_id]
        return df

    def get_time_series_options(self, id: str) -> list:
        df = pd.read_csv(INDICATORS_METADATA, sep=';')
        return list(df['kategorie'])

    def get_hist_data(self, aa_id: str):
        df = pd.read_csv(HISTORIC_VALUES, sep=';')
        df = df[df['kategorie1'].isin(self.time_series_options)]
        return df

    def get_scenarios(self, aa_id: str):
        df = pd.read_csv(SCENARIOS_FILE, sep=';')
        df = df[df['kategorie'].isin(self.time_series_options)]
        return df

    def __repr__(self) -> str:
        return f'ActionArea({self.id}, {self.title})'

    def show_plot(self, plot: dict):
        df = self.hist_values[self.hist_values['kategorie1'] == plot['data_series']]
        if plot['plot_type'] == 'line':
            st.line_chart(df)
        if plot['plot_type'] == 'bar':
            st.bar_chart(df)
        if plot['plot_type'] == 'area':
            settings = json.loads(plot['plot_settings'])
            fig = show_area_plot(df, settings)
        st.plotly_chart(fig)

    def show_settings(self, plot: dict):
        with st.sidebar.expander('⚙️Einstellungen'):
            par1 = st.slider('Parameter 1', min_value=0, max_value=100, value=50)
            par2 = st.slider('Parameter 2', min_value=0, max_value=100, value=50)
            par3 = st.radio('Parameter 3', options=['Option 1', 'Option 2', 'Option 3'])
    
    def get_filter(self, df):
        filter = {}
        with st.sidebar.expander('🔍Filter'):
            filter['kategorie1'] = st.selectbox('Kategorie 1', options=self.time_series_options)
            filter['kategorie2'] = st.selectbox('Kategorie 2', options=self.time_series_options)
            filter['kategorie3'] = st.selectbox('Kategorie 3', options=self.time_series_options)
        return df

    def show_ui(self):
        tabs = st.tabs(['Info', 'Ziele', 'Daten', 'Grafiken', 'Bewertung'])
        with tabs[0]:
            st.markdown(f'## {self.title}')
            st.markdown(self.description)
        with tabs[1]:
            sel_goal = st.selectbox('Ziel', options=self.goals.keys())
            goal = self.goals[sel_goal]
            st.markdown(f'**{sel_goal}: {goal["title"]}**')
            st.markdown(goal['description'])
            if 'monitoring' in goal:
                st.markdown(f'**Methodik:**\n\n{goal["monitoring"]}')
                with st.expander('Faktoren'):
                    df = pd.read_csv(SCENARIOS_FILE, sep=';')
                    df = df[df['goal'] == sel_goal]
                    factors = list(df['factor'].unique())
                    sel_factor = st.selectbox('Faktor', options=factors)
                    df = df[df['factor'] == sel_factor] 
                    st.write(df)
            if 'goal-indicators' in goal:
                st.markdown("---")
                st.markdown("**Ziel-Indikatoren:**")
                for i in goal['goal-indicators']:
                    st.markdown(f"- {i}")
                    with st.expander('Daten & Grafik'):
                        df = pd.read_csv(INDICATORS_METADATA, sep=';')
                        st.write(df)
            if 'time-series' in goal:
                st.markdown("**Auswertungen für die Berechnung der Ziel-Indikatoren**")
                for t2 in goal['time-series']:
                    st.markdown(f"- {t2}")

        with tabs[2]:
            ...
            #sel_dataset = st.selectbox('Datensatz', options=self.time_series_options)
            #df = self.hist_values[self.hist_values['kategorie1'] == sel_dataset]
            #df = self.get_filter(df)
            #st.dataframe(df)
        with tabs[3]:
            if len(self.plot_options) > 0:
                sel_plot = st.selectbox('Graphik', options=self.plot_options)
                plot = self.plots[self.plots['plot_name'] == sel_plot].iloc[0]
                self.show_settings(plot)
                self.show_plot(plot)
            else:
                st.info('Keine Graphiken vorhanden')
        with tabs[4]:
            for key, goal in self.goals.items():
                st.markdown(f'#### {key}')
                st.markdown(f'Bewertung von *{goal["title"]}*')

