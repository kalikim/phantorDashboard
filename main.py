

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


import json

import dash
import dash_bootstrap_components as dbc
# Creates the interactive dashboard using the dash library
import pandas as pd
import plotly.express as px
from dash import dcc
from dash import html
from dash.dependencies import Output, Input
from dash_table import DataTable

# Instantiate the dash app
app = dash.Dash(
    __name__,
    # stylesheet for dash_bootstrap_components
    external_stylesheets=[
        dbc.themes.CERULEAN
    ],
)

# URLs
IMHOTEP_LOGO = "https://imhotep.industries/wp-content/uploads/Imhotep-Industries-Logo-lang.png"
HOME_URL = "https://imhotep.industries/"

# importing the files file with files and geojson files
df = pd.read_csv("world_regions_master1.csv", sep=";")
df.columns = df.columns.str.strip()
# geojson file for saudi
sa_regions_json = json.load(open('rectangle_geojson1.geojson', 'r'))


def create_table(df):
    columns = [
        {"name": "Country",
         "id": "country", "type": "text"},
        {"name": "Place",
         "id": "place", "type": "text"},
        {"name": "Max Annual Water Yield(Litres Per Year)",
         "id": "max_annual_water_yield", "type": "numeric", "format": {'specifier': ','}}
        , {"name": "Annual Power Consumption(MWH Per Year)",
           "id": "annual_power_consumption", "type": "text", "format": {'specifier': ','}},
        {"name": "Max Annual Operating Hours(Hours Per Year)",
         "id": "max_annual_operating_hours", "type": "text", "format": {'specifier': ','}}]

    data = df.sort_values("max_annual_water_yield", ascending=False).to_dict("records")

    return DataTable(
        id='world-table',
        columns=columns,
        data=data,
        fixed_rows={"headers": True},
        active_cell={"row": 0, "column": 0},
        sort_action="native",
        derived_virtual_data=data,
        style_table={
            "minHeight": "80vh",
            "height": "80vh",
            "overflowY": "scroll"
        },
        style_cell={
            "whitespace": "normal",
            "height": "auto",
            "width": "auto",
            "fontFamily": "verdana"
        },
        style_header={
            "textAlign": "center",
            "width": "auto",
            "fontSize": 14
        },
        style_data={
            "fontSize": 10,
            'fontWeight': 'bold'
        },
        style_data_conditional=[
            {
                "if": {"column_id": "country"},
                "width": "80px",
                "textAlign": "left",
                "textDecoration": "underline",
                "cursor": "pointer"
            },
            {
                "if": {"column_id": "place"},
                "width": "100px",
                "textAlign": "left",
                "cursor": "pointer"
            },
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#fafbfb"
            }
        ],
    )


# This is the function to display text on every region on the map

def hover_info(x):
    name = x["place"]
    wateryield = x["max_annual_water_yield"]
    annualpower = x["annual_power_consumption"]
    maxhours = x["max_annual_operating_hours"]

    return (
        f"{name}<br>"
        f"Max Annual Water Yield - {wateryield:,.0f} litres per year<br>"
        f"Annual Power Consumption - {annualpower:,.0f} MWh per year<br>"
        f"Max Annual Operating Hours - {maxhours:,.0f} hours per year<br>"
    )


def create_map(df, geojson, radio_value):
    mycolor = 'OrRd'
    mycolor2 = 'Blues'
    mycolor3 = 'Greens'

    colour_scale = None

    if radio_value == "max_annual_water_yield":
        colour_scale = mycolor2
    elif radio_value == "annual_power_consumption":
        colour_scale = mycolor
    elif radio_value == "max_annual_operating_hours":
        colour_scale = mycolor3

    fig = px.choropleth_mapbox(df,
                               geojson=geojson, color=df[radio_value],
                               locations=df.name,
                               featureidkey="properties.name",
                               color_continuous_scale=colour_scale,
                               labels={'max_annual_water_yield': '',
                                       'annual_power_consumption': '',
                                       'max_annual_operating_hours': ''},

                               hover_name=df.apply(hover_info, axis=1),
                               hover_data={'name': False, 'max_annual_water_yield': False,
                                           'annual_power_consumption': False,
                                           'max_annual_operating_hours': False},

                               opacity=.8, center={'lat': 29.2985, 'lon': 42.5510},

                               mapbox_style="carto-positron", zoom=4)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def create_navbar():
    """
    Creates the navigation bar at the top of the page

    Returns
    -------
    A navigation bar from dash_bootstrap_components
    """

    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src=IMHOTEP_LOGO, height="30px")),
                            dbc.Col(dbc.NavbarBrand("IMHOTEP", className="ms-2")),
                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="https://imhotep.industries/",
                    style={"textDecoration": "none"},
                ),
                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(

                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),
            ]
        ),
        color="primary",
        dark=True,
    )

    return navbar


def create_main_page():
    """
    Large function that creates all the components of the application
    under the navigation bar.

    Other functions are created within this function that are only
        called in create_main_page

    Returns
    -------
    A dash_html_components Div with multiple other Divs
    """
    # Create two pieces of text horizontally just under the navbar

    ######################## Left hand side Components ########################

    # Create the left hand side data tables using the function create_table
    world_table = create_table(df)

    #################### Lower right hand side components ####################

    # Radio buttons for controlling map coloring.
    # dash has radio buttons, but dbc has the ability to
    # control the checked (selected) label.
    radio_items = dbc.RadioItems(
        options=[
            {"label": "Max Annual Water Yield(Litres Per Year)", "value": "max_annual_water_yield"},
            {"label": "Annual Power Consumption(MWH Per Year)", "value": "annual_power_consumption"},
            {"label": "Max Annual Operating Hours(Hours Per Year)", "value": "max_annual_operating_hours"},

        ],
        value="max_annual_water_yield",
        id="map-radio-items",
        style={'display': 'flex',
               'justifyContent': 'space-evenly',
               'backgroundColor': '#212529',
               'color': '#798d8f'},
        labelCheckedStyle={'fontWeight': 800, 'color': 'white'}
    )

    # The choropleth map, like all plotly figures, must be within a dcc.Graph object
    map_graph = dcc.Graph(
        id="map-graph", config={"displayModeBar": False, "responsive": True}
    )

    # major container for all components in the lower right hand side
    map_div = html.Div([radio_items, map_graph], id="map-div")

    ########################### Left side column ###########################

    second_card = dbc.Card(
        dbc.CardBody(
            [
                html.H5("Phantor World Map", className="card-title"),
                html.P(
                    "In response to the increasing demand for new ways of producing drinking water and based on the latest scientific findings, we developed an atmospheric water generator."
                ),

            ]
        )
    )

    ###################### Containers for all components ######################
    row = html.Div(
        [
            dbc.Row(dbc.Col(html.H2("   PHANTOR DASHBOARD"), width={"size": 6, "offset": 3}, )
                    ),
            dbc.Row(
                [
                    dbc.Col(html.Div(), md=1),
                    dbc.Col(html.Div(world_table), md=5),
                    dbc.Col(html.Div(map_div), md=5),
                    dbc.Col(html.Div(), md=1),
                ]
            ),
            dbc.Row(dbc.Col(second_card)),
        ]
    )

    return row


navbar = create_navbar()
container = create_main_page()
app.layout = html.Div([navbar, container])


@app.callback(
    Output("map-graph", "figure"),
    [
        Input("map-radio-items", "value")
    ],
)
def change_map(radio_value):
    return create_map(df, sa_regions_json, radio_value)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    app.run_server(host="localhost", port=8000, debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
