import dash
import dash_daq as daq
import re
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from flask import Flask

from src.app.layout import app_layout
from src.app.controller import setup_callbacks
from src.constants import TAB_COUNT

external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.title = 'Stats Engine'
app.layout = app_layout(TAB_COUNT)
setup_callbacks(app, TAB_COUNT)

server = app.server


if __name__ == '__main__':
    app.run_server(debug=True)