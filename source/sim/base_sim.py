import streamlit as st
from enum import Enum
import os
import pandas as pd

DATA_PATH = './source/data'
TIME_SERIES_FILE = os.path.join(DATA_PATH, 'time_series.csv')
SCENARIO_INTERVALS = os.path.join(DATA_PATH, 'scenario_intervals.csv')


SIM_START_YEAR = 2024
SIM_END_YEAR = 2040

class BaseSimulation():
    def __init__(self, target):
        self.target = target
        self.intervals_df = self.get_intervals()
        self.factor_names = list(self.intervals_df['faktor'].unique())
        self.scenario_names = list(self.intervals_df['szenario'].unique())
    
    def get_intervals(self):
        df = pd.read_csv(SCENARIO_INTERVALS, sep=';')
        df = df[df['ziel'] == self.target]
        return df

    def save_edits(self, df):
        df.to_csv(SCENARIO_INTERVALS, sep=';', index=False)
        self.intervals_df = df

    def save(self):
        '''data is saved in the deleted format with 1 row per factor and base data item
        when read it is unmelted into the pivot format: year, factor1, factor2, time series1 
        '''
        df = pd.DataFrame()
        for scenario in self.scenario_names:
            values = self.result_dict[scenario].reset_index()
            df_factor = values.melt(id_vars=['jahr'], var_name='serie', value_name='wert')
            df_factor['szenario'] = scenario
            df_factor['ziel'] = self.target
            column_order = ['ziel', 'jahr', 'serie', 'wert', 'szenario']
            df_factor = df_factor[column_order]
            df = pd.concat([df, df_factor])
        df.to_csv(os.path.join(DATA_PATH, 'factors.csv'), sep=';', index=False)

    def __repr__(self):
        return f'CarSimulation({self.target})'
    
    def run(self):
        ...
