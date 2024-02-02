import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from enum import Enum
import random
from dataclasses import dataclass

# Initial conditions
TIME_SERIES_FILE = './source/data/time_series.csv'
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

SCENARIOS = {
    Scenario.L.name: {
        "f1": [
            {"from_year": 0, "to_year": 2040, 'from_value': 0.99, 'to_value': 0.99}
        ],
        "f2": [
            {"from_year": 0, "to_year": 2030, 'from_value': 12, 'to_value': 12},
            {"from_year": 2031, "to_year": 2035, 'from_value': 12, 'to_value': 8},
            {"from_year": 2036, "to_year": 2040, 'from_value': 12, 'to_value': 12},
        ],
        "f3": [
            {"from_year": 0, "to_year": 2035, 'from_value': 0.1, 'to_value': 0.99},
            {"from_year": 2036, "to_year": 2040, 'from_value': 0.99, 'to_value': 0.99},
        ],
    },
    Scenario.M.name: {
        "f1": [
            {"from_year": 0, "to_year": 2040, 'from_value': 0.98, 'to_value': 0.98}
        ],
        "f2": [
            {"from_year": 0, "to_year": 2030, 'from_value': 12, 'to_value': 12},
            {"from_year": 2031, "to_year": 2035, 'from_value': 12, 'to_value': 8},
            {"from_year": 2036, "to_year": 2040, 'from_value': 12, 'to_value': 12},
        ],
        "f3": [
            {"from_year": 0, "to_year": 2035, 'from_value': 0.1, 'to_value': 0.99},
            {"from_year": 2036, "to_year": 2040, 'from_value': 0.99, 'to_value': 0.99},
        ],
    },
    Scenario.H.name: {
        "f1": [
            {"from_year": 0, "to_year": 2040, 'from_value': 0.97, 'to_value': 0.97}
        ],
        "f2": [
            {"from_year": 0, "to_year": 2030, 'from_value': 11, 'to_value': 11},
            {"from_year": 2031, "to_year": 2035, 'from_value': 11, 'to_value': 7},
            {"from_year": 2036, "to_year": 2040, 'from_value': 11, 'to_value': 11},
        ],
        "f3": [
            {"from_year": 0, "to_year": 2035, 'from_value': 0.1, 'to_value': 0.99},
            {"from_year": 2036, "to_year": 2040, 'from_value': 0.99, 'to_value': 0.99},
        ],
    },
}

@dataclass
class Car:
    age: int
    is_electric: bool


class CarSimulation:
    def __init__(self):
        self.target_time_series = 13
        self.target_time_series_name = 'PCT_ELECTRIC'
        self.data = self.get_data()
        self.start_year = self.data[(self.data['jahr'] == SIM_START_YEAR - 1)].iloc[0]
        self.factors = self.get_factors()
        st.write(self.start_year)
        self.cars = self.init_cars()


    def get_data(self):
        df = pd.read_csv(TIME_SERIES_FILE, sep=';')
        df['ts_id'] = pd.to_numeric(df['ts_id'])
        df['wert'] = pd.to_numeric(df['wert'])
        base_data_values = [int(member.value) for member in BaseData]
        df = df[df["ts_id"].isin(base_data_values)]
        df['ts_id'] = df['ts_id'].map(lambda x: BaseData(x).name)
        pivot_df = df.pivot(index='jahr', columns='ts_id', values='wert').reset_index()
        result = self.calc_history(pivot_df)
        return result
    
    def calc_history(self, df):
        """
        Calculates the historical percentage of electric usage based on collected data.

        This method calculates the historical percentage of electric usage by dividing the electric usage
        (stored in the 'TS_ELECTRIC' column of the data) by the total usage (stored in the 'TS_TOTAL' column
        of the data). The result is stored in the 'hist_perc_electric' column of the data.

        """
        df[self.target_time_series_name] = df[BaseData.TS_ELECTRIC.name] / df[BaseData.TS_TOTAL.name]
        return df

    def get_factors(self):
            """
            Calculate and return a DataFrame of factors over time. Each factor 

            Returns:
                pandas.DataFrame: A DataFrame containing the factors over time.
            """
            factor_names = list(SCENARIOS[Scenario.L.name].keys())
            scenario_names = [member.name for member in Scenario]
            combined_list = [f"{factor}_{scenario}" for factor in factor_names for scenario in scenario_names]
            df = pd.DataFrame(columns=['jahr'] + combined_list)
            df['jahr'] = range(SIM_START_YEAR, SIM_END_YEAR + 1)
            df.set_index('jahr', inplace=True)
            for scenario_key, scenario in SCENARIOS.items():
                for factor in factor_names:
                    for interval in scenario[factor]:
                        int_start = interval['from_year'] if interval['from_year'] > 0 else SIM_START_YEAR
                        int_end = interval['to_year'] 
                        int_value_start = interval['from_value']
                        int_value_end = interval['to_value']
                        yearly_increase = (int_value_end - int_value_start) / (int_end - int_start)
                        for jahr in range(int_start, int_end + 1):
                            column = f'{factor}_{scenario_key}'
                            if jahr > int_start:
                                df.loc[jahr][column] = df.loc[jahr - 1][column] + yearly_increase
                            else:
                                df.loc[jahr][column] = int_value_start
            st.write(df)
            return df
    
    def predict_base_data(self):
        min_year = self.data['jahr'].min()
        for key, scenario in SCENARIOS.items():
            ...
            #total = last_total * scenario['f1'][year]
    
    def init_cars(self):
        num_electric_start = self.start_year[BaseData.TS_ELECTRIC.name]
        num_non_electric_start = self.start_year[BaseData.TS_TOTAL.name] - num_electric_start
        electric_cars = [Car(age=random.randint(0, MAX_AGE_ELECTRIC), is_electric=True) for _ in range(num_electric_start)]
        non_electric_cars = [Car(age=random.randint(0, MAX_AGE_CAR), is_electric=False) for _ in range(num_non_electric_start)]
        all_cars = electric_cars + non_electric_cars
        random.shuffle(all_cars)
        return all_cars



    def run(self):
        # Simulation over years
        for i, year in enumerate(range(start_year + 1, end_year + 1)):
            age_limit = self.replacement_ages[year]
            # Cars to be replaced
            to_replace = np.sum(self.ages >= age_limit)
            # Number of electric and gas cars added
            electric_added = int(to_replace * self.electric_ratio[year])
            gas_added = to_replace - electric_added

            # Update counts
            self.electric_cars[i + 1] = (
                self.electric_cars[i]
                - np.sum(
                    (self.ages >= age_limit)
                    & (
                        np.linspace(0, 1, total_cars)
                        < (self.electric_cars[i] / total_cars)
                    )
                )
                + electric_added
            )
            self.total_cars_list[i + 1] = total_cars

            # Age the cars and replace
            self.ages = np.where(
                self.ages >= age_limit,
                np.random.randint(0, 2, size=total_cars),
                self.ages + 1,
            )  # Assume new cars have age 0 or 1
        self.ratio_electric_to_total = self.electric_cars / self.total_cars_list

    def plot(self):
        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(
            self.years,
            self.ratio_electric_to_total,
            "-o",
            label="Anteil emissionslos MIV",
        )

        # Setting x-axis to only show full numbers and main ticks every 5 years
        plt.xticks(np.arange(start_year, end_year + 1, 5))

        plt.xlabel("Jahr")
        plt.ylabel("Ratio of Electric Cars to Total Cars")
        plt.title("Electric Car Ratio Over Time")
        plt.grid(True)
        plt.legend()
        return plt

    def save(self):
        df = pd.read_csv("data/time_series.csv")
