import dash
import re
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from src.util import compute



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
  html.H1(
    children='Damage Distribution',
    style={'textAlign': 'center'}
  ),
  dcc.Graph(id='damage-graph'),
  html.Div([
    html.Label('Weapon Skill'),
    dcc.Slider(
      id='attacker-ws',
      min=1,
      max=6,
      marks={i: '{}+'.format(i) for i in range(10)},
      value=3,
      updatemode='drag',
    ),
    html.Label('Toughness'),
    dcc.Slider(
      id='target-toughness',
      min=1,
      max=10,
      marks={i: 'T{}'.format(i) for i in range(10)},
      value=5,
      updatemode='drag',
    ),
    html.Label('Strength'),
    dcc.Slider(
      id='attacker-strength',
      min=1,
      max=20,
      marks={i: 'S{}'.format(i) for i in range(20)},
      value=5,
      updatemode='drag',
    ),
    html.Label('AP Value'),
    dcc.Slider(
      id='attacker-ap',
      min=0,
      max=7,
      marks={i: '-{}'.format(i) for i in range(20)},
      value=2,
      updatemode='drag',
    ),
    html.Label('Save'),
    dcc.Slider(
      id='target-save',
      min=1,
      max=7,
      marks={i: '{}+'.format(i) for i in range(10)},
      value=5,
      updatemode='drag',
    ),
    html.Label('Invuln'),
    dcc.Slider(
      id='target-invuln',
      min=1,
      max=7,
      marks={i: '{}++'.format(i) for i in range(10)},
      value=7,
      updatemode='drag',
    ),
    html.Label('Wounds'),
    dcc.Slider(
      id='target-wounds',
      min=1,
      max=24,
      marks={i: 'W{}'.format(i) for i in range(24)},
      value=7,
      updatemode='drag',
    ),
    html.Label('Shots'),
    dcc.Input(id='attacker-shots', value='2d6', type='text', style={'width': '100%'}),
    html.Label('Damage'),
    dcc.Input(id='attacker-damage', value='3d3', type='text', style={'width': '100%'}),
    html.Label('Modify Shot Volume Rolls'),
    dcc.Dropdown(
      id='shot-modifier',
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
      id='hit-modifier',
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
      id='wound-modifier',
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
  ], style={}),
])

@app.callback(
    Output('damage-graph', 'figure'),
    [
      Input('target-toughness', 'value'),
      Input('target-save', 'value'),
      Input('target-invuln', 'value'),
      Input('target-wounds', 'value'),
      Input('attacker-ws', 'value'),
      Input('attacker-shots', 'value'),
      Input('attacker-strength', 'value'),
      Input('attacker-ap', 'value'),
      Input('attacker-damage', 'value'),
      Input('shot-modifier', 'value'),
      Input('hit-modifier', 'value'),
      Input('wound-modifier', 'value'),
    ])
def update_graph(toughness, save, invuln, wounds, ws, shots, strength, ap, damage,
                 shot_modifier, hit_modifier, wound_modifier):
    values = compute(
      toughness,
      save,
      invuln,
      wounds,
      ws,
      shots,
      strength,
      ap,
      damage,
      shot_modifier,
      hit_modifier,
      wound_modifier,
    )
    return {
        'data': [dict(
            x=[i for i, x in enumerate(values)],
            y=[100*x for i, x in enumerate(values)],
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'}
            }
        )],
        'layout': dict(
            xaxis={
                'title': 'Damage',
                'type': 'linear',
                'range': [0, 24],
                'tickmode': 'linear',
                'tick0': 0,
                'dtick': 1,
            },
            yaxis={
                'title': 'Cumulateive Percentage',
                'type': 'linear',
                'range': [0, 100],
                'tickmode': 'linear',
                'tick0': 0,
                'dtick': 10,

            },
            margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
            hovermode='closest'
        )
    }

def settings_tab():
  return html.Div([
    html.H3('Tab content 2')
  ])


if __name__ == '__main__':
    app.run_server(debug=True)