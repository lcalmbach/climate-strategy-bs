import streamlit as st
import pandas as pd
import os
import random
from plots import scatter_plot

DATA_PATH = './source/data'
GOAL_STATUS_FILE = os.path.join(DATA_PATH, 'goal_status.csv')


class Dashboard():
    def __init__(self):
        self.title = "KSS-Monitoring"
        self.goals_df = self.get_data()

    def get_data(self):
        df = pd.read_csv(GOAL_STATUS_FILE, sep=";")
        return df

    def get_fake_data(self, base):
        x = range(2018, 2023)
        y = [random.randint(0, int(base * 1.5)) for _ in x]
        return pd.DataFrame({'jahr': x, 'wert': y})
    
    def get_random_values(self, base):
        is_value = random.randint(0, int(base * 1.5))
        target_value = random.randint(0, int(base))
        return is_value, target_value

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

    def show_ui(self):
        year, filtered_goals_df = self.filter_data()
        st.markdown(f"### Status der Klimaschutz-Ziele BS im {year}")
        cols = st.columns(3)
        col_id = 0
        for index, row in filtered_goals_df.iterrows():
            with cols[col_id]:
                is_value, target_value = self.get_random_values(row['wert_soll_jahr'])
                st.metric(label=f"Ziel {row['ziel']}, soll: {row['wert_soll_jahr']}",
                          value=is_value,
                          delta=(is_value - target_value),
                          help=f"Hilfetext für Ziel {row['ziel']}")
                self.show_plot(row['wert_soll_jahr'])
                if col_id < 2:
                    col_id += 1
                else:
                    col_id = 0


