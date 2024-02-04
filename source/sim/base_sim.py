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

    def run(self):
        ...
