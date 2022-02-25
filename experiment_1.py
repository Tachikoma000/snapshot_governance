# The purpose of this program is to test out and develop a prototype of a custom dashboard which provides personalized
# metrics for users of Olympus Protocol
# ==================================================
# Import libraries for this app
import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import html, State, Dash, dash_table
from dash.dependencies import Input, Output
import base64
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import math
from millify import millify

from subgrounds.subgraph import SyntheticField, FieldPath
from subgrounds.subgrounds import Subgrounds
from datetime import datetime

from subgrounds.dash_wrappers import Graph
from subgrounds.plotly_wrappers import Figure, Scatter, Indicator

from olympus_subgrounds import sg, protocol_metrics_1year, last_metric, proposals, immediate

# This is a single page app

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])
server = app.server

# Nav bar creation. Something simple for now
navbar = dbc.NavbarSimple(
    children=[],
    brand='Playgrounds Analytics',
    brand_href='#',
    color='#2e343e',
    dark=True,
    fluid=True,
    style={'font-size': '20px',
           'justify - content': 'stretch'
           }
),

sg = Subgrounds()
snapshot = sg.load_subgraph('https://hub.snapshot.org/graphql')

snapshot.Proposal.datetime = SyntheticField(
  lambda timestamp: str(datetime.fromtimestamp(timestamp)),
  SyntheticField.STRING,
  snapshot.Proposal.end,
)

proposals = snapshot.Query.proposals(
  orderBy='created',
  orderDirection='desc',
  first=100,
  where=[
    snapshot.Proposal.space == 'olympusdao.eth',
    snapshot.Proposal.state == 'closed',
  ]
)

proposals_snapshots = sg.query_df([
  proposals.title,
])

proposals_choices = sg.query(proposals.choices)

proposals_choices = pd.DataFrame(proposals_choices, columns = ['option_a', 'option_b', 'option_c', 'option_d', 'option_e'])

olympus_governance_view = pd.concat([proposals_snapshots,proposals_choices], axis=1)


# create the app layout. Nothing too fancy, we just need a way to display the data from the users wallet
app.layout = dbc.Container([
    dbc.Row(navbar),
    dbc.Row([
        dbc.Col([
            dbc.Label('Olympus governance dashboard',
                      style={'font-style': 'normal',
                             'font-weight': '600',
                             'font-size': '64px',
                             'line-height': '96px',
                             'color': '#FFFFFF'
                             }, xs=12, sm=12, md=12, lg=6, xl=6)
        ]),
    ]),
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody(
                    dash_table.DataTable(olympus_governance_view.to_dict('records'),
                                         [{"name": i, "id": i} for i in olympus_governance_view.columns],
                                         page_size=20,
                                         fixed_rows={'headers': True},
                                         style_cell={'textAlign': 'left',
                                                     'border': '1px solid grey'},
                                         style_header={
                                             'backgroundColor': 'rgb(210, 210, 210)',
                                             'color': 'black',
                                             'fontWeight': 'bold'
                                         },
                                         style_data_conditional=[
                                             {
                                                 'if': {'row_index': 'odd'},
                                                 'backgroundColor': 'rgb(220, 220, 220)',
                                             }
                                         ],
                                         ),
                ),
            ]),
        ])
    ]),
    html.Footer('Powered by Subgrounds',
                style={'backgrounds-color': '#2e343e',
                       'color': 'white',
                       'font-size': '20px',
                       'padding': '10px'
                       }),
], style={'backgroundColor': '#2a3847'}, fluid=True)


if __name__ == '__main__':
    app.run_server(debug=True)
