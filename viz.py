
#Imports
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from plotly.colors import qualitative
import sys
from plotly.subplots import make_subplots

# Constants
DATA_FILE = "data/dataframe1.csv"
GENERATION_FILE = "data/dataframe2.csv"
OUTPUT_FILE = "outputs/golden_image.html"

# Color constants
SOLAR_COLOR = '#FF0000'
WIND_COLOR = '#0000FF'

# Approximate geolocation info for key states
STATE_COORDS = {
    'Arizona': {'lat': 34.3, 'lon': -111.7, 'lat_range': 2.5, 'lon_range': 3},
    'California': {'lat': 37.2, 'lon': -119.7, 'lat_range': 3.5, 'lon_range': 4},
    'Colorado': {'lat': 39.0, 'lon': -105.5, 'lat_range': 2.5, 'lon_range': 3},
    'Florida': {'lat': 28.6, 'lon': -81.5, 'lat_range': 3, 'lon_range': 2},
    'Georgia': {'lat': 33.4, 'lon': -83.3, 'lat_range': 2, 'lon_range': 2.5},
    'Illinois': {'lat': 40.0, 'lon': -89.0, 'lat_range': 2, 'lon_range': 2},
    'Iowa': {'lat': 42.0, 'lon': -93.2, 'lat_range': 1.5, 'lon_range': 2.5},
    'Kansas': {'lat': 38.5, 'lon': -98.0, 'lat_range': 2, 'lon_range': 3},
    'Minnesota': {'lat': 46.0, 'lon': -94.0, 'lat_range': 2, 'lon_range': 2.5},
    'Nevada': {'lat': 39.5, 'lon': -116.5, 'lat_range': 3, 'lon_range': 3.5},
    'New Mexico': {'lat': 34.3, 'lon': -106.0, 'lat_range': 2.5, 'lon_range': 3},
    'North Dakota': {'lat': 47.5, 'lon': -100.5, 'lat_range': 2, 'lon_range': 2.5},
    'North Carolina': {'lat': 35.5, 'lon': -79.0, 'lat_range': 2, 'lon_range': 2},
    'Oklahoma': {'lat': 35.5, 'lon': -97.5, 'lat_range': 2, 'lon_range': 2.5},
    'Texas': {'lat': 31.0, 'lon': -99.0, 'lat_range': 4, 'lon_range': 5},
}

# Load and preprocess main data
def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"File not found: {DATA_FILE}")
        sys.exit(1)
    # Aggregate metrics by state
    state_summary = df.groupby('State').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Solar_Plants': 'mean',
        'Wind_Plants': 'mean',
        'Discount': 'mean'
    }).reset_index()
    # Compute total plant count
    state_summary['Total_Plants'] = state_summary['Solar_Plants'] + state_summary['Wind_Plants']
    # Prepare yearly sales data
    yearly = df.groupby(['Year', 'State']).agg({'Sales': 'sum'}).reset_index()
    # Extract dashboard metrics
    stats = {
        'metric1': int(df['Sales'].sum()),
        'metric2': int(df['Profit'].sum()),
        'metric3': round(df['Discount'].mean() * 100, 1)
    }
    return df, state_summary, yearly, stats

# Load generation data (solar/wind in MWh)
def load_generation_data():
    try:
        df_gen = pd.read_csv(GENERATION_FILE)
    except FileNotFoundError:
        print(f"File not found: {GENERATION_FILE}")
        sys.exit(1)
    return df_gen

# Generate random plant coordinates within bounding box
def generate_random_coords(state, num, typ):
    if state not in STATE_COORDS:
        return [], []
    box = STATE_COORDS[state]
    np.random.seed(hash(state + typ) % 2**32)  # Ensure reproducibility per state/type
    lat = np.random.uniform(box['lat'] - box['lat_range'], box['lat'] + box['lat_range'], int(num))
    lon = np.random.uniform(box['lon'] - box['lon_range'], box['lon'] + box['lon_range'], int(num))
    return lat, lon

# Create plant marker traces (solar & wind)
def create_map_traces_per_state(state_df):
    solar_traces = []
    wind_traces = []
    for _, row in state_df.iterrows():
        state = row['State']
        solar_lat, solar_lon, solar_text = [], [], []
        wind_lat, wind_lon, wind_text = [], [], []

        # Solar marker positions
        if row['Solar_Plants'] > 0:
            lat, lon = generate_random_coords(state, row['Solar_Plants'], 'solar')
            solar_lat.extend(lat)
            solar_lon.extend(lon)
            solar_text.extend([f"{state} - Solar Plant"] * len(lat))

        # Wind marker positions
        if row['Wind_Plants'] > 0:
            lat, lon = generate_random_coords(state, row['Wind_Plants'], 'wind')
            wind_lat.extend(lat)
            wind_lon.extend(lon)
            wind_text.extend([f"{state} - Wind Plant"] * len(lat))

        # Add solar markers
        if solar_lat:
            solar_traces.append(go.Scattergeo(
                lon=solar_lon, lat=solar_lat, text=solar_text,
                mode='markers',
                marker=dict(size=8, color=SOLAR_COLOR, opacity=0.85),
                name=f"Solar Plants - {state}",
                hovertemplate='<b>%{text}</b><extra></extra>',
                visible=True,
                showlegend=False
            ))

        # Add wind markers
        if wind_lat:
            wind_traces.append(go.Scattergeo(
                lon=wind_lon, lat=wind_lat, text=wind_text,
                mode='markers',
                marker=dict(size=8, color=WIND_COLOR, opacity=0.85),
                name=f"Wind Plants - {state}",
                hovertemplate='<b>%{text}</b><extra></extra>',
                visible=True,
                showlegend=False
            ))
    return solar_traces, wind_traces

# Create generation clouds per state (proportional to energy)
def create_generation_clouds_per_state(df_gen):
    solar_cloud_traces = []
    wind_cloud_traces = []
    scale_points_per_1000 = 0.05  # Scale energy to number of points
    np.random.seed(42)

    for _, row in df_gen.iterrows():
        state = row['State']
        if state not in STATE_COORDS:
            continue
        box = STATE_COORDS[state]
        solar_energy = row['Solar_Generation_MWh']
        wind_energy = row['Wind_Generation_MWh']
        total_energy = solar_energy + wind_energy
        if total_energy <= 0:
            continue

        total_points = int(total_energy * scale_points_per_1000)
        total_points = max(10, min(total_points, 150))  # Clamp to range
        solar_ratio = solar_energy / total_energy
        wind_ratio = wind_energy / total_energy

        # Split point count by energy type
        solar_points_count = int(total_points * solar_ratio)
        wind_points_count = total_points - solar_points_count

        # Generate cloud points
        solar_lats = np.random.uniform(box['lat'] - box['lat_range'], box['lat'] + box['lat_range'], solar_points_count)
        solar_lons = np.random.uniform(box['lon'] - box['lon_range'], box['lon'] + box['lon_range'], solar_points_count)
        solar_texts = [f"{state} - Solar Generation Cloud<br>Energy: {solar_energy:,} MWh"] * solar_points_count

        wind_lats = np.random.uniform(box['lat'] - box['lat_range'], box['lat'] + box['lat_range'], wind_points_count)
        wind_lons = np.random.uniform(box['lon'] - box['lon_range'], box['lon'] + box['lon_range'], wind_points_count)
        wind_texts = [f"{state} - Wind Generation Cloud<br>Energy: {wind_energy:,} MWh"] * wind_points_count

        # Add clouds with random size and opacity
        solar_cloud_traces.append(go.Scattergeo(
            lon=solar_lons, lat=solar_lats, text=solar_texts,
            mode='markers',
            marker=dict(size=18 + 4 * np.random.rand(solar_points_count),
                        color=SOLAR_COLOR,
                        opacity=0.5 + 0.3 * np.random.rand(solar_points_count)),
            name=f"Solar Clouds - {state}",
            hovertemplate='%{text}<extra></extra>',
            visible=False,
            showlegend=False
        ))

        wind_cloud_traces.append(go.Scattergeo(
            lon=wind_lons, lat=wind_lats, text=wind_texts,
            mode='markers',
            marker=dict(size=18 + 4 * np.random.rand(wind_points_count),
                        color=WIND_COLOR,
                        opacity=0.5 + 0.3 * np.random.rand(wind_points_count)),
            name=f"Wind Clouds - {state}",
            hovertemplate='%{text}<extra></extra>',
            visible=False,
            showlegend=False
        ))

    return solar_cloud_traces, wind_cloud_traces

# Create bubble chart: Sales vs Profit
def create_bubble_chart_per_state(state_df):
    traces = []
    for _, row in state_df.iterrows():
        traces.append(go.Scatter(
            x=[row['Sales']],
            y=[row['Profit']],
            mode='markers',
            marker=dict(
                size=row['Discount'] * 150,
                color=row['Total_Plants'],
                colorscale='blues',
                showscale=False
            ),
            hovertemplate=f"<b>{row['State']}</b><br>Sales: {row['Sales']}<br>Profit: {row['Profit']}<extra></extra>",
            name=f"Bubble - {row['State']}",
            visible=False,
            showlegend=False
        ))
    return traces

# Create line chart: yearly sales trend per state
def create_line_chart_per_state(yearly):
    traces = []
    color_palette = qualitative.Plotly + qualitative.Dark24 + qualitative.Light24
    states = yearly['State'].unique()
    for i, state in enumerate(states):
        data = yearly[yearly['State'] == state]
        traces.append(go.Scatter(
            x=data['Year'],
            y=data['Sales'],
            mode='lines+markers',
            name=f"Line - {state}",
            hovertemplate=f"<b>{state}</b><br>Year: %{{x}}<br>Sales: %{{y}}<extra></extra>",
            line=dict(color=color_palette[i % len(color_palette)]),
            visible=True
        ))
    return traces

# Create grouped bar chart: solar vs wind energy
def create_power_bar_chart_per_state(df_gen):
    states = df_gen['State'].tolist()
    solar_values = df_gen['Solar_Generation_MWh'].tolist()
    wind_values = df_gen['Wind_Generation_MWh'].tolist()

    solar_trace = go.Bar(
        x=states,
        y=[v / 1_000_000 for v in solar_values],  # Convert to million MWh
        name='Solar Power (M MWh)',
        marker_color='orange',
        hovertemplate='<b>%{x}</b><br>Solar Power: %{y:.2f} M MWh<extra></extra>',
        visible=True,
        showlegend=True
    )

    wind_trace = go.Bar(
        x=states,
        y=[v / 1_000_000 for v in wind_values],
        name='Wind Power (M MWh)',
        marker_color='royalblue',
        hovertemplate='<b>%{x}</b><br>Wind Power: %{y:.2f} M MWh<extra></extra>',
        visible=True,
        showlegend=True
    )

    return [solar_trace, wind_trace]
def build_layout():
    # Load datasets and metrics
    df, state_df, yearly, stats = load_data()
    df_gen = load_generation_data()

    # Dashboard title/description (shown as annotation)
    description_text = (
        "State-Level Visualization of <br>Solar and "
        "Wind Energy Infrastructure <br>Across the <br>United States"
    )

    # Set up subplot grid
    fig = make_subplots(
        rows=7, cols=2,
        column_widths=[0.6, 0.4],
        row_heights=[0.6, 0, 0.25, 0.15, 0, 0, 0],
        specs=[
            [{"type": "geo", "rowspan": 2}, {"type": "xy"}],
            [None, None],
            [None, None],
            [{"rowspan": 4, "type": "xy"}, {"rowspan": 4, "type": "xy"}],
            [None, None], [None, None], [None, None]
        ]
    )

    # Generate all trace types
    solar_traces, wind_traces = create_map_traces_per_state(state_df)
    solar_cloud_traces, wind_cloud_traces = create_generation_clouds_per_state(df_gen)
    bubble_traces = create_bubble_chart_per_state(state_df)
    line_traces = create_line_chart_per_state(yearly)
    power_bar_traces = create_power_bar_chart_per_state(df_gen)

    # Add traces to respective positions
    for trace in solar_traces + wind_traces:
        trace.visible = True  # show plants by default
        fig.add_trace(trace, row=1, col=1)
    for trace in solar_cloud_traces + wind_cloud_traces:
        trace.visible = False  # hide energy clouds by default
        fig.add_trace(trace, row=1, col=1)
    for trace in bubble_traces:
        trace.visible = True  # show bubbles by default
        fig.add_trace(trace, row=1, col=2)
    for trace in line_traces:
        trace.visible = False  # hide line chart by default
        fig.add_trace(trace, row=4, col=2)
    for trace in power_bar_traces:
        trace.visible = True
        fig.add_trace(trace, row=4, col=1)

    # Dropdown for all states
    all_states = state_df['State'].tolist()

    # Identify bar chart traces so they are always visible
    bar_trace_indices = [
        i for i, trace in enumerate(fig.data)
        if 'Solar Power' in trace.name or 'Wind Power' in trace.name
    ]

    buttons = []

    # Button: show all states' bubbles & plants
    visible_all = [
        True if i in bar_trace_indices else
        ("Solar Plants" in trace.name or "Wind Plants" in trace.name or "Bubble" in trace.name)
        for i, trace in enumerate(fig.data)
    ]
    buttons.append(dict(label="All States", method="update", args=[{"visible": visible_all}]))

    # One button per state — show that state only
    for state in all_states:
        vis = []
        for i, trace in enumerate(fig.data):
            if i in bar_trace_indices:
                vis.append(True)
            elif state in trace.name:
                vis.append(True)
            else:
                vis.append(False)
        buttons.append(dict(label=state, method="update", args=[{"visible": vis}]))

    # Buttons to toggle between plants/clouds
    plant_cloud_buttons = [
        dict(label="Both Plants", method="update",
             args=[{"visible": [
                 True if i in bar_trace_indices else
                 ("Solar Plants" in t.name or "Wind Plants" in t.name or "Bubble" in t.name)
                 for i, t in enumerate(fig.data)
             ]}]),
        dict(label="Solar Plants Only", method="update",
             args=[{"visible": [
                 True if i in bar_trace_indices else
                 ("Solar Plants" in t.name or "Bubble" in t.name)
                 for i, t in enumerate(fig.data)
             ]}]),
        dict(label="Wind Plants Only", method="update",
             args=[{"visible": [
                 True if i in bar_trace_indices else
                 ("Wind Plants" in t.name or "Bubble" in t.name)
                 for i, t in enumerate(fig.data)
             ]}]),
        dict(label="Solar Energy Accumulation", method="update",
             args=[{"visible": [
                 True if i in bar_trace_indices else
                 ("Solar Clouds" in t.name)
                 for i, t in enumerate(fig.data)
             ]}]),
        dict(label="Wind Energy Accumulation", method="update",
             args=[{"visible": [
                 True if i in bar_trace_indices else
                 ("Wind Clouds" in t.name)
                 for i, t in enumerate(fig.data)
             ]}]),
    ]

    # Set dashboard layout and style
    fig.update_layout(
        paper_bgcolor="#f5f9f6",  # dashboard background
        plot_bgcolor="white",     # plot background
        font=dict(color="#264653"),
        title=dict(
            text="<b>U.S. Renewable Energy Dashboard</b>",
            x=0.5,
            xanchor="center",
            font=dict(size=26)
        ),
        height=950,
        margin=dict(t=110, l=20, r=20, b=20),
        showlegend=True,
        legend=dict(orientation="h", x=0.5, xanchor="center", y=1.02),
        updatemenus=[
            # Top toggle buttons (plants)
            dict(
                type="buttons",
                direction="right",
                x=0.35,
                y=0.42,
                xanchor="center",
                buttons=plant_cloud_buttons[:3],
                showactive=True,
                bgcolor='lightgray',
                pad={"r": 10, "t": 5}
            ),
            # Lower toggle buttons (clouds)
            dict(
                type="buttons",
                direction="right",
                x=0.35,
                y=0.37,
                xanchor="center",
                buttons=plant_cloud_buttons[3:],
                showactive=True,
                bgcolor='lightgray',
                pad={"r": 10, "t": 5}
            ),
            # Dropdown for state selection
            dict(
                buttons=buttons,
                direction="down",
                x=0.23,
                y=1.06,
                xanchor="left",
                showactive=True,
            )
        ]
    )

    # Configure geo map style
    fig.update_geos(
        scope='usa',
        projection_type='albers usa',
        showland=True,
        landcolor='rgb(217, 217, 217)'
    )

    # Set axis labels
    fig.update_xaxes(title_text='Sales', row=1, col=2)
    fig.update_yaxes(title_text='Profit', row=1, col=2)
    fig.update_xaxes(title_text='Year', row=4, col=2)
    fig.update_yaxes(title_text='Sales', row=4, col=2)
    fig.update_xaxes(title_text='States', row=4, col=1)
    fig.update_yaxes(title_text='Power', row=4, col=1)

    # Add descriptive annotations for charts
    fig.add_annotation(
        text=description_text,
        xref='paper', yref='paper',
        x=0.01, y=0.36,
        showarrow=False,
        align='left',
        bordercolor='black',
        borderwidth=1,
        bgcolor='lightyellow',
        font=dict(size=14)
    )

    fig.add_annotation(
        text="<b>Bubble Chart</b><br>Size represents Discount<br>Color = Total Plants<br>X: Sales, Y: Profit",
        xref='paper', yref='paper',
        x=0.71, y=0.98,
        showarrow=False,
        bgcolor='lightyellow',
        font=dict(size=12)
    )

    fig.add_annotation(
        text="<b>Select a State to View Detailed Energy Analysis:</b>",
        xref='paper', yref='paper',
        x=0, y=1.05,
        showarrow=False,
        font=dict(size=12)
    )

    fig.add_annotation(
        text="<b>Line Chart</b><br>Sales trends over Years per State",
        xref='paper', yref='paper',
        x=0.78, y=0.27,
        showarrow=False,
        bgcolor='lightyellow',
        font=dict(size=12)
    )

    fig.add_annotation(
        text="<b>Bar Graph</b><br>Solar and Wind Power Generation<br>(in Million MWh) per State",
        xref='paper', yref='paper',
        x=0.28, y=0.2,
        showarrow=False,
        bgcolor='lightyellow',
        font=dict(size=12)
    )

    return fig

# Entry point to build and save dashboard
if __name__ == "__main__":
    fig = build_layout()
    fig.write_html(OUTPUT_FILE)
    print(f"Dashboard saved to {OUTPUT_FILE}")
