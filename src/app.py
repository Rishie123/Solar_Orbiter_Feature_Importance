import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Load the combined DataFrame
df = pd.read_csv('combined_shap_values.csv')


# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Prepare data by type
def prepare_data(df, type_label):
    # Filter DataFrame by the specified type
    df_filtered = df[df['Type'] == type_label]
    # Create pivot table
    pivot_df = df_filtered.pivot_table(
        values='Normalized_Importance', index='Duration', columns='Feature', aggfunc='sum')
    # Filter out columns where all values are zero
    pivot_df = pivot_df.loc[:, (pivot_df != 0).any(axis=0)]
    return pivot_df


# Create Plotly Express graphs for each type
def create_figure(data, title):
    fig = px.area(data, title=title)
    fig.update_layout(yaxis_title='Normalized Importance', xaxis_title='Time of Heater Profile(sec)')
    return fig

# Types to include in the dashboard
types = ['IBS_R', 'IBS_N', 'IBS_T', 'OBS_R', 'OBS_N', 'OBS_T']
figures = [create_figure(prepare_data(df, type_label), f'Cumulative Normalized Feature Importance of Heater Profiles {type_label}') for type_label in types]

# Define the layout of the app to include a graph for each type
app.layout = html.Div([dcc.Graph(figure=fig) for fig in figures])

# Run the server
if __name__ == '__main__':
    app.run_server(debug=True, port=8071)
