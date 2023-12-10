# Import required libraries
import pandas as pd
import dash
# import dash_html_components as html
# import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px
from dash import html, dcc, Dash

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
# max_payload = spacex_df['Payload Mass (kg)'].max()
# min_payload = spacex_df['Payload Mass (kg)'].min()
spacex_df['Payload Mass (kg)'] = pd.to_numeric(spacex_df['Payload Mass (kg)'], errors='coerce')
spacex_df['Payload Mass (kg)'] = spacex_df['Payload Mass (kg)'].fillna(0).astype(int)

max_payload = int(spacex_df['Payload Mass (kg)'].max())
min_payload = int(spacex_df['Payload Mass (kg)'].min())

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                  dcc.Dropdown(id='site-dropdown',
                options=[
                    {'label': 'All Sites', 'value': 'ALL'},
                    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                ],
                value='ALL',
                placeholder="place holder here",
                searchable=True
                ),


                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
        id='payload-slider',
        
        step=1000,
        marks={i: str(i) for i in range(min_payload, max_payload + 1, 500)},
        value=[min_payload,max_payload]
    ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(site):
    if site == 'ALL':
        # Total successful launches for all sites
        total_success = spacex_df[spacex_df['class'] == 1]['class'].count()
        total_failed = spacex_df[spacex_df['class'] == 0]['class'].count()

        labels = ['Successful', 'Failed']
        sizes = [total_success, total_failed]
        colors = ['#66b3ff', '#ff9999']
        
        return px.pie(values=sizes, names=labels, color_discrete_sequence=colors,
                      title='Total Launches - Success vs. Failed')
    else:
        # Success vs. Failed counts for a specific site
        site_data = spacex_df[spacex_df['Launch Site'] == site]
        site_success = site_data[site_data['class'] == 1]['class'].count()
        site_failed = site_data[site_data['class'] == 0]['class'].count()

        labels = ['Successful', 'Failed']
        sizes = [site_success, site_failed]
        colors = ['#66b3ff', '#ff9999']

        return px.pie(values=sizes, names=labels, color_discrete_sequence=colors,
                      title=f'{site} - Success vs. Failed')

# Task 4: Callback Function for Scatter Chart
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'), 
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_data = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
        (spacex_df['Payload Mass (kg)'] <= payload_range[1])
    ]
    if selected_site != 'ALL':
        filtered_data = filtered_data[filtered_data['Launch Site'] == selected_site]

    return px.scatter(filtered_data, x='Payload Mass (kg)', y='class',
                      color='Booster Version Category',
                      title='Correlation between Payload and Launch Success')

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)