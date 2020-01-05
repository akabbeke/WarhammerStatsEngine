import dash
import dash_daq
import re
import dash_core_components as dcc
import dash_html_components as html


def tab_disable_input(n):
  return html.Div([
    html.Br(),
    dash_daq.ToggleSwitch( # pylint: disable=not-callable
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
      multi=True,
      style={'width': '100%'},
    ),
  ])

def modify_save_input(n):
  return html.Div([
    html.Label('Modify Save Rolls'),
    dcc.Dropdown(
      persistence=True,
      id='save_mods_{}'.format(n),
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
      multi=True,
      style={'width': '100%'},
    ),
  ])

def generate_options(base_options, selected):
  options = []
  for option, label, lim in base_options:
    existing_ids = []
    for sel_id in selected:
      match = re.match('{}_(\d+)'.format(option), sel_id)
      if match:
        existing_ids.append(int(match.groups()[0]))
    max_id = max(existing_ids + [0])
    if len(existing_ids) < lim:
      ids = existing_ids + [max_id + 1]
    else:
      ids = existing_ids
    for i in ids:
      options += [{'label': label, 'value': '{}_{}'.format(option, i)}]
  return options

def generate_modify_shot_options(selected):
  base_options = [
    ['re_roll_1s', 'Re-roll 1\'s', 1],
    ['re_roll_dice', 'Re-roll all rolls', 1],
  ]
  return generate_options(base_options, selected)

def generate_modify_hit_options(selected):
  base_options = [
    ['re_roll_1s', 'Re-roll 1\'s', 1],
    ['re_roll_failed', 'Re-roll failed rolls', 1],
    ['re_roll_dice', 'Re-roll all rolls', 1],
    ['add_1', 'Add +1', 4],
    ['sub_1', 'Sub -1', 5],
    ['mod_extra_hit_6_1', '+1 hit on 6+', 3],
    ['mod_extra_hit_5_1', '+1 hit on 5+', 3],
    ['extra_hit_6_1', '+1 hit on 6', 3],
    ['extra_hit_5_1', '+1 hit on 5 or 6', 3],
    ['mod_extra_shot_6_1', '+1 shot on 6+', 3],
    ['mod_extra_shot_5_1', '+1 shot on 5+', 3],
    ['extra_shot_6_1', '+1 shot on 6', 3],
    ['extra_shot_6_1', '+1 shot on 5 or 6', 3],
    ['mod_mortal_wound_6_1', 'MW on 6+', 4],
    ['mod_mortal_wound_5_1', 'MW on 5+', 4],
    ['mortal_wound_6_1', 'MW on 6', 4],
    ['mortal_wound_5_1', 'MW on 5 or 6', 4],
  ]
  return generate_options(base_options, selected)

def generate_modify_wound_options(selected):
  base_options = [
    ['re_roll_1s', 'Re-roll 1\'s', 1],
    ['re_roll_failed', 'Re-roll failed rolls', 1],
    ['re_roll_dice', 'Re-roll all rolls', 1],
    ['add_1', 'Add +1', 4],
    ['sub_1', 'Sub -1', 4],
    ['mod_mortal_wound_6_1', 'MW on 6+', 4],
    ['mod_mortal_wound_5_1', 'MW on 5+', 4],
    ['mortal_wound_6_1', 'MW on 6', 4],
    ['mortal_wound_5_1', 'MW on 5 or 6', 4],
    ['haywire', 'Haywire', 1]
  ]
  return generate_options(base_options, selected)

def generate_modify_save_options(selected):
  base_options = [
    ['re_roll_1s', 'Re-roll 1\'s', 1],
    ['re_roll_failed', 'Re-roll failed rolls', 1],
    ['re_roll_dice', 'Re-roll all rolls', 1],
    ['ignore_ap_1', 'Ignore AP -1', 1],
    ['ignore_ap_2', 'Ignore AP -2', 1],
    ['ignore_invuln', 'Ignore Invuln', 1],
    ['add_1', '+1 Save', 4],
    ['sub_1', '-1 Save', 5],
    ['add_inv_1', '+1 Invuln', 4],
    ['sub_inv_1', '-1 Invuln', 5],
  ]
  return generate_options(base_options, selected)

def generate_modify_damage_options(selected):
  base_options = [
    ['re_roll_1s', 'Re-roll 1\'s', 1],
    ['re_roll_dice', 'Re-roll all rolls', 1],
    ['minimum_3', 'Minimum 3', 1],
    ['melta', 'Melta', 1],
    ['half_damage', 'Half Damage', 1],
    ['add_1', 'Add +1', 4],
    ['sub_1', 'Sub -1', 5],

  ]
  return generate_options(base_options, selected)

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
    modify_save_input(n),
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
    'save_mods_{}'.format(i),
    'damage_mods_{}'.format(i),
  ]

def graph_inputs(tab_count):
  inputs = []
  for i in range(1, tab_count+1):
    inputs += gen_tab_inputs(i)
  return inputs

def header():
  return dcc.Markdown('''
### Warhammer Stats Engine
The graph is the probability that the attack will do at least that much damage. 100% chance to do at least zero damage, and it drops from there.
''')


def footer():
  return dcc.Markdown('''
### Also:
For the shots and damage characteristic, you can either use a fixed number or XdY notation to represent a rolling
X dice with Y sides. You can also add modifiers to the hit and wound rolls that stack (e.g. re-rolling 1's to hit and -1 to hit).
You can also download an image of the graph by clicking the camera icon while hovering over the graph.

##### Updates:
* Removed the +/- 2 and 3 modifiers and instead you can now add +/-1 multiple times.
* Added the 'exploding dice' mechanic for hit rolls. You can stack them so for example two "+1 hit on 6+" will yield +2 hits on a 6+.
* Added mortal wound generation for hit and wound rolls
* Added Haywire

This is still very much a work in progress, and there are probably still some bugs. I'm /u/Uily on Reddit, so please let me know if you find any.
If you want to contribute [you can find the repo here](https://github.com/akabbeke/WarhammerStatsEngine).

##### Todo:
* Figure out feed-forward abilities like rend
* Replace the frontend with an actual frontend instead of this cobbled together dash frontend
* Figure out a way to allow users to create units and have all their weapons output combined (Which russ is the best russ?)
* ???


There are no **Ads** funding this, so please don't be a dick. Otherwise, I hope you find this useful!
''')

def graph_figure_template(data, max_len=24):
  return {
    'data': data,
    'layout': {
      'xaxis': {
          'title': 'Damage',
          'type': 'linear',
          'range': [0, max_len],
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

def damage_graph(tab_count):
  return dcc.Graph(
    id='damage-graph',
    figure=graph_figure_template([{}] * tab_count)
  )

def settings_tabs(tab_count):
  tabs = []
  for i in range(1, tab_count+1):
    tabs.append(
      dcc.Tab(
        id='tab_{}'.format(i),
        label='Profile {}'.format(i),
        children=[tab_settings(i)]
      )
    )
  return dcc.Tabs(tabs)

def app_layout(tab_count):
  return html.Div([
    header(),
    damage_graph(tab_count),
    settings_tabs(tab_count),
    footer(),
  ])