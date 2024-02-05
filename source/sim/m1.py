import streamlit as st
import numpy as np
import pandas as pd
from enum import Enum
import random
from dataclasses import dataclass
import sys
import os
from pathlib import Path
from sim.base_sim import (BaseSimulation,TIME_SERIES_FILE,SIM_START_YEAR,SIM_END_YEAR,DATA_PATH)
# Add the parent directory to sys.path
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Now you can import plot_lines from plots.py
from plots import line_chart


# used for initializing the MIV carpool
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


@dataclass
class Car:
    age: int
    is_electric: bool


class CarSimulation(BaseSimulation):
    def __init__(self, target):
        super().__init__(target)

        self.target_time_series = 13
        self.target_time_series_name = 'PCT_ELECTRIC'
        self.data = self.get_data()
        self.start_year = self.data[(self.data['jahr'] == SIM_START_YEAR - 1)].iloc[0]
        self.result_dict = self.get_factors()
        self.cars = []

    def predict_base_values(self):
        """
        extrapolates the base values for the simulation period.

        This method iterates over each scenario and calculates the base values
        based on the previous year's value and a factor 'f1'.

        Returns:
            None
        """
        for scenario_key in self.scenario_names:
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

        for scenario_key in self.scenario_names:
            interval_df = self.intervals_df[self.intervals_df['szenario'] == scenario_key]
            df = init_results(self.factor_names)
            for factor in self.factor_names:
                interval_df = self.intervals_df[(self.intervals_df['szenario'] == scenario_key) & (self.intervals_df['faktor'] == factor)]
                for index, interval in interval_df.iterrows():
                    int_start = (
                        interval['jahr_von']
                        if interval['jahr_von'] > 0
                        else SIM_START_YEAR
                    )
                    int_end = interval['jahr_bis']
                    int_value_start = interval['wert_von']
                    int_value_end = interval['wert_bis']
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
        
        for scenario in self.scenario_names:
            cars = self.cars.copy()
            values = self.result_dict[scenario]
            values[BaseData.TS_ELECTRIC_RATIO.name] = 0
            values[BaseData.TS_ELECTRIC.name] = 0
            values[BaseData.TS_TOTAL.name] = 0
            values['new_gas'] = 0
            values['new_electric'] = 0
            values['old_cars'] = 0
            values['miv_gas'] = 0
            for year in range(SIM_START_YEAR, SIM_END_YEAR + 1):
                new_car_num = round(len(cars) * values.loc[year, 'f1'])
                car_num = len(cars)
                age_limit = values.loc[year, 'f2']
                # remove cars older than age_limit
                cars = [car for car in cars if car.age < age_limit]
                to_replace = new_car_num - len(cars)
                # after an increase in car age cobined with a decline in predicted cars, the number of cars to be replaced
                # is negative and cars need to be removed
                if to_replace < 0:
                    cars_sorted_by_age = sorted(cars, key=lambda car: car.age, reverse=True)
                    cars = cars_sorted_by_age[-(to_replace):]
                    to_replace = 0
                old_car_num = car_num - len(cars)
                # Number of electric and gas cars added
                electric_added = round(to_replace * values.loc[year, 'f3'])
                gas_added = to_replace - electric_added

                # Increment age for each remaining car
                cars = [
                    Car(age=car.age + 1, is_electric=car.is_electric) for car in cars
                ]
                # Add new electric cars
                cars.extend(
                    [Car(age=0, is_electric=True) for _ in range(electric_added)]
                )
                # Add new gas cars
                cars.extend([Car(age=0, is_electric=False) for _ in range(gas_added)])
                values.loc[year, BaseData.TS_ELECTRIC.name] = len(
                    [car for car in cars if car.is_electric]
                )
                # values.loc[year, 'new_gas'] = gas_added
                # values.loc[year, 'new_electric'] = electric_added
                # values.loc[year, 'old_cars'] = old_car_num
                # values.loc[year, 'miv_gas'] = len([car for car in cars if not car.is_electric])
                values.loc[year, BaseData.TS_TOTAL.name] = len(cars)
            values[self.target_time_series_name] = (
                    100 * values[BaseData.TS_ELECTRIC.name] / values[BaseData.TS_TOTAL.name]
                )
            # st.write(values)

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
        for scenario in self.scenario_names:
            df = self.result_dict[scenario].copy().reset_index()
            df = df[['jahr', self.target_time_series_name]]
            df['szenario'] = scenario
            results.append(df)
        plot_df = pd.concat(results)
        fig = line_chart(plot_df, settings)
        return fig, plot_df
    
    def get_factors(self):
        '''data read from the melted format and unmeldetd into a dict with one dataframe per scenario
        '''
        df = pd.read_csv(os.path.join(DATA_PATH, 'factors.csv'), sep=';')
        my_scenarios = {}
        for scenario in self.scenario_names:
            df_scenario = df[df['szenario'] == scenario]
            df_scenario = df_scenario.pivot(index='jahr', columns='serie', values='wert')
            df_scenario = df_scenario.rename_axis(None, axis=1)
            my_scenarios[scenario] = df_scenario
        return my_scenarios

    

    