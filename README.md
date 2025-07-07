# 🌞💨 Energy Dashboard Visualization

This project provides an interactive energy analytics dashboard that visualizes renewable energy plant distributions, profit and sales performance, and sales trends across U.S. states using `Plotly`.

## 📊 Features

- **Map Visualization**: Displays the locations of solar and wind plants across U.S. states using approximated geographic coordinates.
- **Revenue vs Profit Bubble Chart**: Shows the relationship between total sales, profit, plant count, and discounts by state.
- **Sales Trend Line Chart**: Tracks annual sales trends for each state.
- **Interactive Dashboard**: Combines all three visualizations in a single scrollable HTML dashboard.
- **Auto-launch**: Automatically opens the dashboard in your default browser once rendered.

---

## 📁 Project Structure

/energy-dashboard: README.md                             # Main project folder containing metadata and setup files

/energy-dashboard/data: dataframe1.csv, dataframe2.csv                       # Input data files (CSV format with energy stats by state/year)

/energy-dashboard /outputs: golden_image.html                                # Auto-generated dashboard output (opens in browser) 

/energy-dashboard/scripts: viz.py, data_gen.py                               # Python scripts: main visualization + data generator


---

## 🛠️ Requirements

- Python 3.11+
- Plotly
- Pandas
- NumPy


**Data Format**:

The CSV (dataframe1.csv) must contain at least the following columns:

| Column Name            | Description                   |
| ---------------------- | ----------------------------- |
| `State`                | U.S. state name               |
| `Year`                 | Year of record                |
| `Sales`                | Sales amount                  |
| `Profit`               | Profit amount                 |
| `Solar_Plants`         | Number of solar plants        |
| `Wind_Plants`          | Number of wind plants         |
| `Discount`             | Average discount percentage   |
| `Solar_Generation_MWh` | Solar power generation in MWh |
| `Wind_Generation_MWh`  | Wind power generation in MWh  |

> 🔄 The dashboard uses `Total_Plants`, calculated as:  
> `Total_Plants = Solar_Plants + Wind_Plants`

> 📍 The dashboard also assigns geographic coordinates (`Latitude` and `Longitude`) based on the `State` name internally using predefined mappings—no need to include them in the CSV.

---

### ✅ Example Row


`State,Year,Solar_Generation_MWh,Wind_Generation_MWh,Sales,Profit,Discount,Solar_Plants,Wind_Plants
Texas,2024,36125,27521,2400000,1250000,3.5,25,40`


**Installing Dependencies**

In the command prompt just run this code:
`pip install pandas plotly numpy`


**How to Run: **

`python scripts/data_gen.py` // first this file to generate the data

`python scripts/viz.py `// then this one to create a web page with dashboard.

📷 **Sample Output**

![image](https://github.com/user-attachments/assets/4ad53c63-ca43-4b5c-831c-2d2005195ad9)

![image](https://github.com/user-attachments/assets/d9595e34-134c-430c-b59a-434f6d2975b1)




