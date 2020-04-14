import dash
import dash_daq as daq
import re
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from flask import Flask

from engine.app.layout import Layout
from engine.app.controllers import CallbackController
from engine.constants import TAB_COUNT, WEAPON_COUNT

external_stylesheets = [
  dbc.themes.COSMO,
  {
    'href': 'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
    'rel': 'stylesheet',
    'integrity': 'sha384-50oBUHEmvpQ+1lW4y57PTFmhCaXp0ML5d60M1M7uH2+nqUivzIebhndOJK28anvf',
    'crossorigin': 'anonymous'
  },
]

external_scripts=[
  'https://cdn.jsdelivr.net/gh/akabbeke/WarhammerStatsEngine/gtag.js'
  'https://kit.fontawesome.com/6ded1a5b89.js',
]

app = dash.Dash(
  __name__,
  external_stylesheets=external_stylesheets,
  external_scripts=external_scripts,
)

app.title = 'Stats Engine'
app.config.suppress_callback_exceptions = True
app.layout = Layout(tab_count=TAB_COUNT, weapon_count=WEAPON_COUNT).layout()
CallbackController(app, TAB_COUNT, WEAPON_COUNT).setup_callbacks()

server = app.server


if __name__ == '__main__':
    app.run_server(debug=True)