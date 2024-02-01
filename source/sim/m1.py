import numpy as np
import matplotlib.pyplot as plt

# Initial conditions
total_cars = 60000
start_year = 2020
end_year = 2040
initial_electric_cars = 2000
initial_gas_cars = total_cars - initial_electric_cars
target_time_series = 13

class CarSimulation:
    def __init__(self):
        # Distribute age randomly from 0 to 12 years
        self.ages = np.random.randint(0, 13, total_cars)

        # Calculate replacement ages for each year
        self.replacement_ages = {year: 12 if year < 2031 or year > 2035 else 10 for year in range(start_year, end_year + 1)}

        # Calculate ratio of electric to gas cars in new cars for each year
        self.electric_ratio = {year: 0.1 + (0.88 * (year - start_year) / (2035 - start_year)) if year <= 2035 else 0.98 for year in range(start_year, end_year + 1)}

        # Initialize counts
        self.electric_cars = np.zeros(end_year - start_year + 1)
        self.total_cars_list = np.zeros_like(self.electric_cars)

        # Initial condition
        self.electric_cars[0] = initial_electric_cars
        self.total_cars_list[0] = total_cars
        self.ratio_electric_to_total =  np.zeros_like(self.electric_cars)
        self.years = np.arange(start_year, end_year + 1)

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
            self.electric_cars[i + 1] = self.electric_cars[i] - np.sum((self.ages >= age_limit) & (np.linspace(0, 1, total_cars) < (self.electric_cars[i]/total_cars))) + electric_added
            self.total_cars_list[i + 1] = total_cars
            
            # Age the cars and replace
            self.ages = np.where(self.ages >= age_limit, np.random.randint(0, 2, size=total_cars), self.ages + 1)  # Assume new cars have age 0 or 1
        self.ratio_electric_to_total = self.electric_cars / self.total_cars_list
        
    def plot(self):
        # Plotting
        plt.figure(figsize=(10, 6))
        plt.plot(self.years, self.ratio_electric_to_total, '-o', label='Anteil emissionslos MIV')

        # Setting x-axis to only show full numbers and main ticks every 5 years
        plt.xticks(np.arange(start_year, end_year + 1, 5))

        plt.xlabel('Jahr')
        plt.ylabel('Ratio of Electric Cars to Total Cars')
        plt.title('Electric Car Ratio Over Time')
        plt.grid(True)
        plt.legend()
        return plt

    def save(self):
        ...