import pandas as pd  # Pandas for data manipulation
import dash  # Dash library for creating web applications
from dash import dcc, html, dash_table  # Components for building layout
from dash.dependencies import Input, Output  # Callbacks to update layout based on user input
import plotly.express as px  # Plotly Express for creating interactive visualizations
import plotly.graph_objects as go  # Plotly Graph Objects for more control over visualizations

# Load the dataset
data_path = "Solar_Orbiter_with_anomalies.csv"  # Path to dataset file
solar_data = pd.read_csv(data_path)  # Read dataset into DataFrame

# Initialize the Dash app
app = dash.Dash(__name__, title="Solar Orbiter Data Visualization") # Title of the Dash app which is showed in the browser tab
server = app.server

# Layout of the Dash app
app.layout = html.Div([
    html.H1("Solar Orbiter Instrument Data Visualization", style={'text-align': 'center'}),  # Title

    # Checklist to select instruments
    dcc.Checklist(
        id='instrument-checklist',  # Component ID
        options=[{'label': col, 'value': col} for col in solar_data.columns[1:-2]],  # Options for checklist
        value=[solar_data.columns[1]],  # Default selected value (first instrument)
        inline=True
    ),

    # Date range picker
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=solar_data['Date'].min(),  # Minimum date allowed
        max_date_allowed=solar_data['Date'].max(),  # Maximum date allowed
        start_date=solar_data['Date'].min(),  # Default start date
        end_date=solar_data['Date'].max()  # Default end date
    ),

    # Two rows, each containing two graphs
    html.Div([
        html.Div([dcc.Graph(id='time-series-chart')], className="six columns"),  # Time Series Chart
        html.Div([dcc.Graph(id='correlation-heatmap')], className="six columns"),  # Correlation Heatmap
    ], className="row"),
    html.Div([
        html.Div([dcc.Graph(id='anomaly-score-chart')], className="six columns"),  # Anomaly Score Chart
    ], className="row"),

    html.Div(id='anomaly-stats', style={'margin-top': '20px', 'text-align': 'center'}),  # Anomaly Stats
    html.Iframe(
        srcDoc=open("shap_values_plot.html").read(),
        style={"height": "500px", "width": "100%"}
    )
])

# Callbacks to update graphs
@app.callback(
    [Output('time-series-chart', 'figure'),
     Output('correlation-heatmap', 'figure'),
     Output('anomaly-score-chart', 'figure')],
    [Input('instrument-checklist', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_graphs(selected_instruments, start_date, end_date):
    filtered_data = solar_data[(solar_data['Date'] >= start_date) & (solar_data['Date'] <= end_date)]  # Filtering data based on selected date range
    
    # Time Series Chart
    time_series_fig = go.Figure()  # Creating a new figure for time series chart
    for instrument in selected_instruments:
        time_series_fig.add_trace(
            go.Scatter(
                x=filtered_data['Date'],  # X-axis data
                y=filtered_data[instrument],  # Y-axis data
                mode='lines+markers',  # Display mode
                name=instrument  # Instrument name
            )
        )
    time_series_fig.update_layout(title="Time Series of Selected Instruments")  # Updating layout of time series chart

    # Correlation Heatmap
    correlation_fig = go.Figure(
        go.Heatmap(
            z=filtered_data[selected_instruments].corr(),  # Calculating correlation matrix
            x=selected_instruments,  # X-axis labels
            y=selected_instruments,  # Y-axis labels
            colorscale='Viridis'  # Color scale
        )
    )
    correlation_fig.update_layout(title="Correlation Heatmap")  # Updating layout of correlation heatmap

    # Anomaly Score Chart
    anomaly_score_fig = px.line(
        filtered_data,
        x='Date',  # X-axis data
        y='anomaly_score',  # Y-axis data
        title="Anomaly Scores Over Time (Lower scores indicate more anomalies)"  # Chart title
    )

    return time_series_fig, correlation_fig, anomaly_score_fig  # Return updated figures

if __name__ == "__main__":
    app.run_server(debug=True, port=8071)  # Start the Dash server in debug mode with a specific port
