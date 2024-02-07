import streamlit as st
import pandas as pd
import os
import random
from plots import scatter_plot

DATA_PATH = './source/data'
DATASETS_FILE = os.path.join(DATA_PATH, 'dataset.csv')
TIME_SERIES_FILE = os.path.join(DATA_PATH, 'time_series.csv')
GOAL_STATUS_FILE = os.path.join(DATA_PATH, 'goal_status.csv')
TIME_SERIES_GOALS_FILE = os.path.join(DATA_PATH, 'time_series_goal.csv')

class DataBrowser():
    def __init__(self):
        self.datasets_df = self.get_datasets()
        self.time_series_df = self.get_time_series()
        self.time_series_goals = self.get_time_series_goals()

    def get_time_series_goals(self):
        df = pd.read_csv(TIME_SERIES_GOALS_FILE, sep=";")
        return df
    
    def get_datasets(self):
        df = pd.read_csv(DATASETS_FILE, sep=";")
        return df

    def get_time_series(self):
        df = pd.read_csv(TIME_SERIES_FILE, sep=";")
        return df

    def filter_data(self):
        aa_dict = {
            'all': 'Alle',
            'M': 'Mobilität',
            'G': 'Gebäude',
            'B': 'Bauen',
            'W': 'Wirtschaft',
            'E': 'Energieversorgung',
            'EN': 'Abfall & Net',
            'L': 'Landwirtschaft'
        }
        with st.sidebar:
            with st.expander("🔎Filter", expanded=True):
                year = st.selectbox(
                    label='Jahr',
                    options=self.goals_df['jahr'].unique()
                )
                action_area = st.selectbox(
                    label='Handlungsfeld',
                    options=aa_dict.keys(),
                    format_func=lambda x: aa_dict[x]
                )
        if action_area == 'all':
            df = self.goals_df
        else:
            df = self.goals_df[self.goals_df['ziel'].str.startswith(action_area)]
        return year, df
    
    def show_plot(self, base):
        df = self.get_fake_data(base)
        settings = {
            'x': 'jahr',
            'y': 'wert',
            'xaxis_title': 'Jahr',
            'yaxis_title': 'Wert',
            'line': {'color': 'red', 'dash': 'dash'},
            'width': 300, 
            'height': 300
        }
        fig = scatter_plot(df, settings)
        st.plotly_chart(fig, width=300, height=300)

    def show_data(self, dataset, unit):
        data_df = self.time_series_df[self.time_series_df['ts_id'] == dataset]
        data_df.drop(columns=['ts_id'], inplace=True)
        data_df.reset_index(drop=True, inplace=True)
        data_df['einheit'] = unit
        st.dataframe(data_df)

    def show_ui(self):
        st.markdown("### Datenbrowser")
        ds_options = dict(zip(self.datasets_df['id'], self.datasets_df['name']))
        dataset = st.selectbox(
            label='Datensatz',
            options=ds_options.keys(),
            format_func=lambda x: ds_options[x]
        )
        ds = self.datasets_df[self.datasets_df['id'] == dataset].iloc[0]
        st.write(f'Beschreibung: {ds["description"]}')
        used_in = self.time_series_goals[self.time_series_goals['ts_id'] == dataset]
        used_in = list(used_in['goal'].unique())
        used_in = [str(x) for x in used_in]
        used_in = ', '.join(used_in)
        st.write(f'Wird verwendet in: {used_in}')
        self.show_data(dataset, ds["unit"])
        

