import dash
import dash_daq as daq
import re
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from flask import Flask

from src.util import compute

TAB_COUNT = 4

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Stats Engine'
server = app.server



def tab_disable_input(n):
  return html.Div([
    html.Br(),
    daq.ToggleSwitch(
      id='enable_{}'.format(n),
      value=n < 3,
      label='Disable/Enable',
      labelPosition='left'
    ),

  ])

def ws_input(n):
  return html.Div([
    html.Label('Weapon Skill'),
    dcc.Slider(
      persistence=True,
      id='ws_{}'.format(n),
      min=1,
      max=6,
      marks={i: '{}+'.format(i) for i in range(10)},
      value=max(1, n%6),

    ),
  ])

def toughtness_input(n):
  return html.Div([
    html.Label('Toughness'),
    dcc.Slider(
      persistence=True,
      id='toughness_{}'.format(n),
      min=1,
      max=10,
      marks={i: 'T{}'.format(i) for i in range(10)},
      value=max(1, (1+n)%6),

    ),
  ])

def strength_input(n):
  return html.Div([
    html.Label('Strength'),
    dcc.Slider(
      persistence=True,
      id='strength_{}'.format(n),
      min=1,
      max=20,
      marks={i: 'S{}'.format(i) for i in range(20)},
      value=5,

    ),
  ])

def ap_input(n):
  return html.Div([
    html.Label('AP Value'),
    dcc.Slider(
      persistence=True,
      id='ap_{}'.format(n),
      min=0,
      max=7,
      marks={i: '-{}'.format(i) for i in range(20)},
      value=2,

    ),
  ])

def save_input(n):
  return html.Div([
    html.Label('Save'),
    dcc.Slider(
      persistence=True,
      id='save_{}'.format(n),
      min=1,
      max=7,
      marks={i: '{}+'.format(8-i) for i in range(10)},
      value=5,

    ),
  ])

def invuln_input(n):
  return html.Div([
    html.Label('Invuln'),
    dcc.Slider(
      persistence=True,
      id='invuln_{}'.format(n),
      min=1,
      max=7,
      marks={i: '{}++'.format(8-i) for i in range(10)},
      value=0,

    ),
  ])

def fnp_input(n):
  return html.Div([
    html.Label('FNP'),
    dcc.Slider(
      persistence=True,
      id='fnp_{}'.format(n),
      min=1,
      max=7,
      marks={i: '{}+++'.format(8-i) for i in range(10)},
      value=0,

    ),
  ])

def wounds_input(n):
  return html.Div([
    html.Label('Wounds'),
    dcc.Slider(
      persistence=True,
      id='wounds_{}'.format(n),
      min=1,
      max=24,
      marks={i: 'W{}'.format(i) for i in range(24)},
      value=7,

    ),
  ])

def shots_input(n):
  return html.Div([
    html.Label('Shots'),
    dcc.Input(
      persistence=True,
      id='shots_{}'.format(n),
      value=['2d3', '12', 'd6', '7'][(n-1)%4],
      type='text',
      style={'width': '100%'}
    ),
  ])

def damage_input(n):
  return html.Div([
    html.Label('Damage'),
    dcc.Input(
      persistence=True,
      id='damage_{}'.format(n),
      value=['d3', '3', '2d6', '3d4'][(n-1)%4],
      type='text',
      style={'width': '100%'}
    ),
  ])

def modify_shot_input(n):
  return html.Div([
    html.Label('Modify Shot Volume Rolls'),
    dcc.Dropdown(
      persistence=True,
      id='shot_mods_{}'.format(n),
      options=[
          {'label': 'Re-roll 1\'s', 'value': 're_roll_1s'},
          {'label': 'Re-roll all dice', 'value': 're_roll_dice'}
      ],
      multi=True,
      style={'width': '100%'},
    ),
  ])

def modify_hit_input(n):
  return html.Div([
    html.Label('Modify Hit Rolls'),
    dcc.Dropdown(
      persistence=True,
      id='hit_mods_{}'.format(n),
      options=[
          {'label': 'Re-roll 1\'s', 'value': 're_roll_1s'},
          {'label': 'Re-roll failed rolls', 'value': 're_roll_failed'},
          {'label': 'Re-roll all rolls', 'value': 're_roll_dice'},
          {'label': 'Add +1', 'value': 'add_1'},
          {'label': 'Add +2', 'value': 'add_2'},
          {'label': 'Add +3', 'value': 'add_3'},
          {'label': 'Sub -1', 'value': 'sub_1'},
          {'label': 'Sub -2', 'value': 'sub_2'},
          {'label': 'Sub -3', 'value': 'sub_3'},
      ],
      multi=True,
      style={'width': '100%'},
    ),
  ])

def modify_wound_input(n):
  return html.Div([
    html.Label('Modify Wound Rolls'),
    dcc.Dropdown(
      persistence=True,
      id='wound_mods_{}'.format(n),
      options=[
          {'label': 'Re-roll 1\'s', 'value': 're_roll_1s'},
          {'label': 'Re-roll failed rolls', 'value': 're_roll_failed'},
          {'label': 'Re-roll all rolls', 'value': 're_roll_dice'},
          {'label': 'Add +1', 'value': 'add_1'},
          {'label': 'Add +2', 'value': 'add_2'},
          {'label': 'Add +3', 'value': 'add_3'},
          {'label': 'Sub -1', 'value': 'sub_1'},
          {'label': 'Sub -2', 'value': 'sub_2'},
          {'label': 'Sub -3', 'value': 'sub_3'},
      ],
      multi=True,
      style={'width': '100%'},
    ),
  ])

def modify_damage_input(n):
  return html.Div([
    html.Label('Modify Damage Rolls'),
    dcc.Dropdown(
      persistence=True,
      id='damage_mods_{}'.format(n),
      options=[
          # {'label': 'Re-roll one dice', 'value': 're_roll_one_dice'},
          {'label': 'Re-roll 1\'s', 'value': 're_roll_1s'},
          {'label': 'Re-roll all dice', 'value': 're_roll_dice'},
          {'label': 'Melta', 'value': 'melta'},
          {'label': 'Add +1', 'value': 'add_1'},
          {'label': 'Add +2', 'value': 'add_2'},
          {'label': 'Add +3', 'value': 'add_3'},
          {'label': 'Sub -1', 'value': 'sub_1'},
          {'label': 'Sub -2', 'value': 'sub_2'},
          {'label': 'Sub -3', 'value': 'sub_3'},
      ],
      multi=True,
      style={'width': '100%'},
    ),
  ])

def tab_settings(n):
  return html.Div([
    tab_disable_input(n),
    ws_input(n),
    toughtness_input(n),
    strength_input(n),
    ap_input(n),
    save_input(n),
    invuln_input(n),
    fnp_input(n),
    wounds_input(n),
    shots_input(n),
    damage_input(n),
    modify_shot_input(n),
    modify_hit_input(n),
    modify_wound_input(n),
    modify_damage_input(n),
    html.Br()
  ], style={})

def gen_tab_inputs(i):
  return [
    'enable_{}'.format(i),
    'ws_{}'.format(i),
    'toughness_{}'.format(i),
    'strength_{}'.format(i),
    'ap_{}'.format(i),
    'save_{}'.format(i),
    'invuln_{}'.format(i),
    'fnp_{}'.format(i),
    'wounds_{}'.format(i),
    'shots_{}'.format(i),
    'damage_{}'.format(i),
    'shot_mods_{}'.format(i),
    'hit_mods_{}'.format(i),
    'wound_mods_{}'.format(i),
    'damage_mods_{}'.format(i),
  ]

def graph_inputs():
  inputs = []
  for i in range(1, TAB_COUNT+1):
    inputs += gen_tab_inputs(i)
  return inputs

def belrb():
  return dcc.Markdown('''
#### 40k Stats Engine

This started as a personal project of mine to build a computer model for the probability distributions
of dice rolls in 40k. I found a pretty efficient way to do this without the need for a Monte Carlo
approach, so I decided to turn his into a web app for the community.

The graph produced below is the probability that the attack will do at least that much damage. It's why you always
have a 100% chance to do zero damage, and it drops from there.

For the shots and damage characteristic, you can either use a fixed number or `XdY` notation to represent a rolling
X dice with Y sides. You can also add modifiers to the hit and wound rolls that stack (e.g. re-rolling 1's to hit and -1 to hit).
''')


def second_berb():
  return dcc.Markdown('''
#### Also:

This is still very much a work in progress, and there are probably still some bugs. I'm /u/Uily on Reddit, so please let me know if you find any.
If you want to contribute [you can find the repo here](https://github.com/akabbeke/WarhammerStatsEngine). I'm still
working on implementing more features such as exploding 6's and a few others.

There are no **Ads** funding this, so please don't be a dick. Otherwise, I hope you find this useful!
''')


app.layout = html.Div([
  belrb(),
  dcc.Graph(id='damage-graph'),
  dcc.Tabs([
    dcc.Tab(
      id='tab_{}'.format(i),
      label='Profile {}'.format(i),
      children=[tab_settings(i)]) for i in range(1, TAB_COUNT+1)],
    ),
  second_berb(),
])

def parse_args(args):
  mapped_args = []
  for i in range(0, TAB_COUNT):
    tab_dict = {}
    tab_inputs = gen_tab_inputs(i)
    trim_length = -1 * len('-{}'.format(i))
    for j, input_name in enumerate(tab_inputs):
      tab_dict[input_name[:trim_length]] = args[(len(tab_inputs)*i) + j]
    mapped_args.append(tab_dict)
  return mapped_args

def generate_data(args):
  graph_data = []
  for i, kwargs in enumerate(parse_args(args)):
    values = compute(**kwargs)
    graph_data.append({
      'x': [i for i, x in enumerate(values)],
      'y': [100*x for i, x in enumerate(values)],
      'name': 'P{}'.format(i + 1),
    })
  return graph_data


@app.callback(Output('damage-graph', 'figure'), [Input(x, 'value') for x in graph_inputs()])
def update_graph(*args):
  return {
    'data': generate_data(args),
    'layout': {
      'xaxis': {
          'title': 'Damage',
          'type': 'linear',
          'range': [0, 24],
          'tickmode': 'linear',
          'tick0': 0,
          'dtick': 1,
      },
      'yaxis': {
          'title': 'Cumulateive Percentage',
          'type': 'linear',
          'range': [0, 100],
          'tickmode': 'linear',
          'tick0': 0,
          'dtick': 10,
      },
      # 'transition': {'duration': 50},
      'margin': {'l': 40, 'b': 40, 't': 10, 'r': 0},
      'hovermode': 'x'
    }
  }


if __name__ == '__main__':
    app.run_server(debug=True)