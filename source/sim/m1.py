import streamlit as st
import numpy as np
import pandas as pd
from enum import Enum
import random
from dataclasses import dataclass
import sys
import os
from pathlib import Path

# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Now you can import plot_lines from plots.py
from plots import line_chart

# Initial conditions
DATA_PATH = './source/data'
TIME_SERIES_FILE = os.path.join(DATA_PATH, 'time_series.csv')

SIM_START_YEAR = 2024
SIM_END_YEAR = 2040

MAX_AGE_ELECTRIC = 3
MAX_AGE_CAR = 12


class BaseData(Enum):
    TS_TOTAL = 4
    TS_ELECTRIC = 5
    TS_AGE_RENEW = 6
    TS_ELECTRIC_RATIO = 14


class Scenario(Enum):
    L = 10
    M = 11
    H = 12


# f1: annula growth of total cars
# f2: replacement age in years for cars
# f3: ratio of electric cars in newly bought cars
SCENARIOS = {
    Scenario.L.name: {
        'f1': [
            {'from_year': 0, 'to_year': 2040, 'from_value': 0.995, 'to_value': 0.995}
        ],
        'f2': [
            {'from_year': 0, 'to_year': 2030, 'from_value': 12, 'to_value': 12},
            {'from_year': 2031, 'to_year': 2035, 'from_value': 12, 'to_value': 8},
            {'from_year': 2036, 'to_year': 2040, 'from_value': 12, 'to_value': 12},
        ],
        'f3': [
            {'from_year': 0, 'to_year': 2035, 'from_value': 0.1, 'to_value': 0.99},
            {'from_year': 2036, 'to_year': 2040, 'from_value': 0.99, 'to_value': 0.99},
        ],
    },
    Scenario.M.name: {
        'f1': [
            {'from_year': 0, 'to_year': 2040, 'from_value': 0.990, 'to_value': 0.990}
        ],
        'f2': [
            {'from_year': 0, 'to_year': 2030, 'from_value': 12, 'to_value': 12},
            {'from_year': 2031, 'to_year': 2035, 'from_value': 12, 'to_value': 8},
            {'from_year': 2036, 'to_year': 2040, 'from_value': 12, 'to_value': 12},
        ],
        'f3': [
            {'from_year': 0, 'to_year': 2035, 'from_value': 0.1, 'to_value': 0.99},
            {'from_year': 2036, 'to_year': 2040, 'from_value': 0.99, 'to_value': 0.99},
        ],
    },
    Scenario.H.name: {
        'f1': [
            {'from_year': 0, 'to_year': 2040, 'from_value': 0.985, 'to_value': 0.985}
        ],
        'f2': [
            {'from_year': 0, 'to_year': 2030, 'from_value': 11, 'to_value': 11},
            {'from_year': 2031, 'to_year': 2035, 'from_value': 11, 'to_value': 7},
            {'from_year': 2036, 'to_year': 2040, 'from_value': 11, 'to_value': 11},
        ],
        'f3': [
            {'from_year': 0, 'to_year': 2035, 'from_value': 0.1, 'to_value': 0.99},
            {'from_year': 2036, 'to_year': 2040, 'from_value': 0.99, 'to_value': 0.99},
        ],
    },
}


@dataclass
class Car:
    age: int
    is_electric: bool


class CarSimulation:
    def __init__(self):
        self.target = 'M1'
        self.factor_names = list(SCENARIOS[Scenario.L.name].keys())
        self.target_time_series = 13
        self.target_time_series_name = 'PCT_ELECTRIC'
        self.data = self.get_data()
        self.start_year = self.data[(self.data['jahr'] == SIM_START_YEAR - 1)].iloc[0]
        self.result_dict = self.get_factors()
        self.cars = []

    def predict_base_values(self):
        for scenario_key, scenario in SCENARIOS.items():
            table = self.result_dict[scenario_key]
            table[BaseData.TS_TOTAL.name] = None
            table.loc[SIM_START_YEAR, BaseData.TS_TOTAL.name] = self.start_year[
                BaseData.TS_TOTAL.name
            ]

            for year in range(SIM_START_YEAR + 1, SIM_END_YEAR + 1):
                table.loc[year, BaseData.TS_TOTAL.name] = round(
                    table.loc[year - 1, BaseData.TS_TOTAL.name] * table['f1'][year]
                )

    def get_data(self):
        '''
        Retrieves and processes data from a CSV file.

        Returns:
            result (DataFrame): Processed data in a DataFrame format.
        '''
        df = pd.read_csv(TIME_SERIES_FILE, sep=';')
        df['ts_id'] = df['ts_id'].astype(int)
        df['jahr'] = df['jahr'].astype(int)
        df['wert'] = df['wert'].astype(float)
        base_data_values = [int(member.value) for member in BaseData]
        df = df[df['ts_id'].isin(base_data_values)]
        df['ts_id'] = df['ts_id'].map(lambda x: BaseData(x).name)
        pivot_df = df.pivot(index='jahr', columns='ts_id', values='wert').reset_index()
        result = self.calc_history(pivot_df)
        return result

    def calc_history(self, df) -> pd.DataFrame:
        '''
        Calculates the historical percentage of electric usage based on collected data.

        This method calculates the historical percentage of electric usage by dividing the electric usage
        (stored in the 'TS_ELECTRIC' column of the data) by the total usage (stored in the 'TS_TOTAL' column
        of the data). The result is stored in the 'hist_perc_electric' column of the data.

        '''
        df[self.target_time_series_name] = (
            df[BaseData.TS_ELECTRIC.name] / df[BaseData.TS_TOTAL.name]
        )
        return df
    
    def calc_factors(self) -> pd.DataFrame:
        '''
        Calculate and return a DataFrame of factors over time. Each factor

        Returns:
            pandas.DataFrame: A DataFrame containing the factors over time.
        '''

        def init_results(column_names: list) -> pd.DataFrame:
            df = pd.DataFrame(columns=['jahr'] + column_names)
            df['jahr'] = range(SIM_START_YEAR, SIM_END_YEAR + 1)
            df.set_index('jahr', inplace=True)
            return df

        my_scenarios = {}

        for scenario_key, scenario in SCENARIOS.items():
            df = init_results(self.factor_names)
            for factor in self.factor_names:
                for interval in scenario[factor]:
                    int_start = (
                        interval['from_year']
                        if interval['from_year'] > 0
                        else SIM_START_YEAR
                    )
                    int_end = interval['to_year']
                    int_value_start = interval['from_value']
                    int_value_end = interval['to_value']
                    yearly_increase = (int_value_end - int_value_start) / (
                        int_end - int_start
                    )
                    for jahr in range(int_start, int_end + 1):
                        if jahr > int_start:
                            df.loc[jahr][factor] = (
                                df.loc[jahr - 1][factor] + yearly_increase
                            )
                        else:
                            df.loc[jahr][factor] = int_value_start
            my_scenarios[scenario_key] = df
        return my_scenarios

    def predict_base_data(self):
        min_year = self.data['jahr'].min()
        for key, scenario in SCENARIOS.items():
            ...
            # total = last_total * scenario['f1'][year]

    def init_cars(self):
        num_electric_start = int(self.start_year[BaseData.TS_ELECTRIC.name])
        num_non_electric_start = int(
            self.start_year[BaseData.TS_TOTAL.name] - num_electric_start
        )
        electric_cars = [
            Car(age=random.randint(0, MAX_AGE_ELECTRIC), is_electric=True)
            for _ in range(num_electric_start)
        ]
        non_electric_cars = [
            Car(age=random.randint(0, MAX_AGE_CAR), is_electric=False)
            for _ in range(num_non_electric_start)
        ]
        all_cars = electric_cars + non_electric_cars
        random.shuffle(all_cars)
        return all_cars

    def run(self):
        self.result_dict = self.calc_factors()
        self.predict_base_values()
        self.cars = self.init_cars()
        
        for scenario in SCENARIOS:
            cars = self.cars.copy()
            values = self.result_dict[scenario]
            values[BaseData.TS_ELECTRIC.name] = 0
            for year in range(SIM_START_YEAR, SIM_END_YEAR + 1):
                age_limit = values.loc[year, 'f2']
                cars = [car for car in cars if car.age < age_limit]
                to_replace = int(values.loc[year, BaseData.TS_TOTAL.name] - len(cars))

                # Number of electric and gas cars added
                electric_added = round(to_replace * values.loc[year, 'f3'])
                gas_added = to_replace - electric_added
                values.loc[year, BaseData.TS_ELECTRIC.name] = len(
                    [car for car in cars if car.is_electric]
                )

                # Increment age for each car
                cars = [
                    Car(age=car.age + 1, is_electric=car.is_electric) for car in cars
                ]
                # Add new electric cars
                cars.extend(
                    [Car(age=0, is_electric=True) for _ in range(electric_added)]
                )
                # Add new gas cars
                cars.extend([Car(age=0, is_electric=False) for _ in range(gas_added)])
                values[self.target_time_series_name] = (
                    100 * values[BaseData.TS_ELECTRIC.name] / values[BaseData.TS_TOTAL.name]
                )

    def get_plot(self):
        settings = {
            'x': 'jahr',
            'y': self.target_time_series_name,
            'color': 'szenario',
            'xaxis_title': 'Jahr',
            'yaxis_title': 'Anteil emissionslos Fzg MIV %',
            'color_name': 'Szenario',
            'h_line': 97,
        }
        results = []
        for scenario in SCENARIOS:
            df = self.result_dict[scenario].reset_index().copy()
            df['szenario'] = scenario
            results.append(df)
        fig = line_chart(pd.concat(results), settings)
        return fig
    
    def get_scenarios_df(self):
        df = pd.DataFrame()
        for secenario_key, scenario in SCENARIOS.items():
            for factor, intervals in scenario.items():
                for interval in intervals:
                    row = pd.DataFrame({
                        'szenario': [secenario_key],
                        'faktor': [factor],
                        'jahr_von': [interval['from_year']],
                        'jahr_bis': [interval['to_year']],
                        'wert_von': [interval['from_value']],
                        'wert_bis': [interval['to_value']]
                    })
                    df = pd.concat([df, row])
        return df


        for scenario in SCENARIOS:
            values = self.result_dict[scenario].reset_index()
            df = pd.concat([df, values])
        return df
    
    def get_factors(self):
        '''data read from the melted format and unmeldetd into a dict with one dataframe per scenario
        '''
        df = pd.read_csv(os.path.join(DATA_PATH, 'factors.csv'), sep=';')
        my_scenarios = {}
        for scenario in SCENARIOS:
            df_scenario = df[df['szenario'] == scenario]
            df_scenario = df_scenario.pivot(index='jahr', columns='serie', values='wert')
            df_scenario = df_scenario.rename_axis(None, axis=1)
            my_scenarios[scenario] = df
        return my_scenarios

    def save(self):
        '''data is saved in the mleted format with 1 row per factor and base data item
        when read it is unmelted into the pivot format: year, factor1, factor2, time series1 
        '''
        df = pd.DataFrame()
        for scenario in SCENARIOS:
            values = self.result_dict[scenario].reset_index()
            df_factor = values.melt(id_vars=['jahr'], var_name='serie', value_name='wert')
            df_factor['szenario'] = scenario
            df_factor['ziel'] = self.target
            column_order = ['ziel', 'jahr', 'serie', 'wert', 'szenario']
            df_factor = df_factor[column_order]
            df = pd.concat([df, df_factor])
        df.to_csv(os.path.join(DATA_PATH, 'factors.csv'), sep=';', index=False)
