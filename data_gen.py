import pandas as pd
import numpy as np
import os

# Seed for reproducibility
np.random.seed(4)

states = [
    'Arizona', 'California', 'Colorado', 'Florida', 'Georgia',
    'Illinois', 'Iowa', 'Kansas', 'Minnesota', 'Nevada',
    'New Mexico', 'North Dakota', 'North Carolina', 'Oklahoma', 'Texas'
]
years = [2019, 2020, 2021, 2022, 2023, 2024]

main_data = []
generation_data = []

for state in states:
    for year in years:
        base_sales = np.random.randint(50000, 150000)

        if state in ['California', 'Arizona', 'Nevada', 'Florida']:
            solar_plants = np.random.randint(20, 50)
            wind_plants = np.random.randint(5, 20)
        elif state in ['Iowa', 'Kansas', 'Oklahoma', 'North Dakota']:
            solar_plants = np.random.randint(5, 20)
            wind_plants = np.random.randint(20, 50)
        else:
            solar_plants = np.random.randint(10, 30)
            wind_plants = np.random.randint(10, 30)

        # Generation values
        solar_gen = solar_plants * np.random.randint(1000, 3000)
        wind_gen = wind_plants * np.random.randint(2000, 5000)

        # Main dataset (without generation columns)
        main_data.append({
            'State': state,
            'Year': year,
            'Sales': base_sales,
            'Profit': np.random.randint(5000, 30000),
            'Discount': round(np.random.uniform(0.1, 0.5), 2),
            'Solar_Plants': solar_plants,
            'Wind_Plants': wind_plants,
            'Total_Plants': solar_plants + wind_plants
        })

        # Generation dataset
        generation_data.append({
            'State': state,
            'Year': year,
            'Solar_Generation_MWh': solar_gen,
            'Wind_Generation_MWh': wind_gen
        })

# Save both datasets
os.makedirs("data", exist_ok=True)
pd.DataFrame(main_data).to_csv("data/dataframe1.csv", index=False)
pd.DataFrame(generation_data).to_csv("data/dataframe2.csv", index=False)

print("'dataframe1.csv' saved (no power columns)")
print("'dataframe2.csv' saved (only generation data)")
