import dash
import re
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from flask import Flask

from src.util import compute



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

def graph_settings(n):
  return html.Div([
    html.Label('Weapon Skill'),
    dcc.Slider(
      persistence=True,
      id='attacker-ws-{}'.format(n),
      min=1,
      max=6,
      marks={i: '{}+'.format(i) for i in range(10)},
      value=3,
      updatemode='drag',
    ),
    html.Label('Toughness'),
    dcc.Slider(
      persistence=True,
      id='target-toughness-{}'.format(n),
      min=1,
      max=10,
      marks={i: 'T{}'.format(i) for i in range(10)},
      value=5,
      updatemode='drag',
    ),
    html.Label('Strength'),
    dcc.Slider(
      persistence=True,
      id='attacker-strength-{}'.format(n),
      min=1,
      max=20,
      marks={i: 'S{}'.format(i) for i in range(20)},
      value=5,
      updatemode='drag',
    ),
    html.Label('AP Value'),
    dcc.Slider(
      persistence=True,
      id='attacker-ap-{}'.format(n),
      min=0,
      max=7,
      marks={i: '-{}'.format(i) for i in range(20)},
      value=2,
      updatemode='drag',
    ),
    html.Label('Save'),
    dcc.Slider(
      persistence=True,
      id='target-save-{}'.format(n),
      min=1,
      max=7,
      marks={i: '{}+'.format(8-i) for i in range(10)},
      value=5,
      updatemode='drag',
    ),
    html.Label('Invuln'),
    dcc.Slider(
      persistence=True,
      id='target-invuln-{}'.format(n),
      min=1,
      max=7,
      marks={i: '{}++'.format(8-i) for i in range(10)},
      value=0,
      updatemode='drag',
    ),
    html.Label('FNP'),
    dcc.Slider(
      persistence=True,
      id='target-fnp-{}'.format(n),
      min=1,
      max=7,
      marks={i: '{}+++'.format(8-i) for i in range(10)},
      value=0,
      updatemode='drag',
    ),
    html.Label('Wounds'),
    dcc.Slider(
      persistence=True,
      id='target-wounds-{}'.format(n),
      min=1,
      max=24,
      marks={i: 'W{}'.format(i) for i in range(24)},
      value=7,
      updatemode='drag',
    ),
    html.Label('Shots'),
    dcc.Input(persistence=True, id='attacker-shots-{}'.format(n), value='2d6', type='text', style={'width': '100%'}),
    html.Label('Damage'),
    dcc.Input(persistence=True, id='attacker-damage-{}'.format(n), value='3d3', type='text', style={'width': '100%'}),
    html.Label('Modify Shot Volume Rolls'),
    dcc.Dropdown(
      persistence=True,
      id='shot-modifier-{}'.format(n),
      options=[
          {'label': 'Re-roll one dice', 'value': 're_roll_one_dice'},
          {'label': 'Re-roll 1\'s', 'value': 're_roll_1s'},
          {'label': 'Re-roll all dice', 'value': 're_roll_dice'}
      ],
      multi=True,
      style={'width': '100%'},
    ),
    html.Label('Modify Hit Rolls'),
    dcc.Dropdown(
      persistence=True,
      id='hit-modifier-{}'.format(n),
      options=[
          {'label': 'Re-roll 1\'s', 'value': 're_roll_1s'},
          {'label': 'Re-roll failed rolls', 'value': 're_roll_failed'},
          {'label': 'Re-roll all rolls', 'value': 're_roll'},
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
    html.Label('Modify Wound Rolls'),
    dcc.Dropdown(
      persistence=True,
      id='wound-modifier-{}'.format(n),
      options=[
          {'label': 'Re-roll 1\'s', 'value': 're_roll_1s'},
          {'label': 'Re-roll failed rolls', 'value': 're_roll_failed'},
          {'label': 'Re-roll all rolls', 'value': 're_roll'},
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
    html.Label('Modify Damage Rolls'),
    dcc.Dropdown(
      persistence=True,
      id='damage-modifier-{}'.format(n),
      options=[
          {'label': 'Re-roll one dice', 'value': 're_roll_one_dice'},
          {'label': 'Re-roll 1\'s', 'value': 're_roll_1s'},
          {'label': 'Re-roll all dice', 'value': 're_roll_dice'},
          {'label': 'Melta', 'value': 'roll_two_choose_highest'},
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
    html.Br()
  ], style={})

app.layout = html.Div([
  html.H1(
    children='Probability of at least N Damage',
    style={'textAlign': 'center'}
  ),
  dcc.Graph(id='damage-graph'),
  dcc.Tabs([
    dcc.Tab(label='Attack A', children=[graph_settings(1)]),
    dcc.Tab(label='Attack B', children=[graph_settings(2)]),
  ]),
])

@app.callback(
    Output('damage-graph', 'figure'),
    [
      Input('target-toughness-1', 'value'),
      Input('target-save-1', 'value'),
      Input('target-invuln-1', 'value'),
      Input('target-fnp-1', 'value'),
      Input('target-wounds-1', 'value'),
      Input('attacker-ws-1', 'value'),
      Input('attacker-shots-1', 'value'),
      Input('attacker-strength-1', 'value'),
      Input('attacker-ap-1', 'value'),
      Input('attacker-damage-1', 'value'),
      Input('shot-modifier-1', 'value'),
      Input('hit-modifier-1', 'value'),
      Input('wound-modifier-1', 'value'),
      Input('damage-modifier-1', 'value'),

      Input('target-toughness-2', 'value'),
      Input('target-save-2', 'value'),
      Input('target-invuln-2', 'value'),
      Input('target-fnp-2', 'value'),
      Input('target-wounds-2', 'value'),
      Input('attacker-ws-2', 'value'),
      Input('attacker-shots-2', 'value'),
      Input('attacker-strength-2', 'value'),
      Input('attacker-ap-2', 'value'),
      Input('attacker-damage-2', 'value'),
      Input('shot-modifier-2', 'value'),
      Input('hit-modifier-2', 'value'),
      Input('wound-modifier-2', 'value'),
      Input('damage-modifier-2', 'value'),

    ])
def update_graph(toughness_1, save_1, invuln_1, fnp_1, wounds_1, ws_1, shots_1, strength_1, ap_1, damage_1,
                 shot_modifier_1, hit_modifier_1, wound_modifier_1, damage_modifier_1, toughness_2, save_2,
                 invuln_2, fnp_2, wounds_2, ws_2, shots_2, strength_2, ap_2, damage_2, shot_modifier_2,
                 hit_modifier_2, wound_modifier_2, damage_modifier_2):
    values_1 = compute(
      toughness_1,
      8-save_1,
      8-invuln_1,
      8-fnp_1,
      wounds_1,
      ws_1,
      shots_1,
      strength_1,
      ap_1,
      damage_1,
      shot_modifier_1,
      hit_modifier_1,
      wound_modifier_1,
      damage_modifier_1,
    )
    values_2 = compute(
      toughness_2,
      8-save_2,
      8-invuln_2,
      8-fnp_2,
      wounds_2,
      ws_2,
      shots_2,
      strength_2,
      ap_2,
      damage_2,
      shot_modifier_2,
      hit_modifier_2,
      wound_modifier_2,
      damage_modifier_2,
    )
    return {
      'data': [
        {
          'x': [i for i, x in enumerate(values_1)],
          'y': [100*x for i, x in enumerate(values_1)],
          'name': 'Attack A',
        },
        {
          'x': [i for i, x in enumerate(values_2)],
          'y': [100*x for i, x in enumerate(values_2)],
          'name': 'Attack B',
        }
      ],
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