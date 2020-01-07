import dash
import dash_daq
import re
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc


class Layout(object):
  def __init__(self, tab_count):
    self._tab_count = tab_count

def tab_disable_input(n):
  checklist = dbc.Checklist(
    options=[{"label": "Enable", "value": 'enabled'}],
    value=['enabled'] if n == 1 else [],
    id='enable_{}'.format(n),
    switch=True,
    inline=True,
  )
  foo = dbc.Input(
    type="text",
    id='tab_name_{}'.format(n),
    value='Profile {}'.format(n),
    debounce=True,
    minLength=2,
  )
  return dbc.InputGroup([dbc.InputGroupAddon(checklist), foo], className="mb-2",)

def attack_input(n):
  # dropdown_menu_items = [dbc.DropdownMenuItem("Apply to all", 'apply_target_{}'.format(n))]
  return dbc.InputGroup(
    [
      # dbc.DropdownMenu(dropdown_menu_items, label="Target", addon_type="prepend", direction="right"),
      dbc.InputGroupAddon("Target", addon_type="prepend"),
      dbc.InputGroupAddon("T", addon_type="prepend"),
      dbc.Select(
        id='toughness_{}'.format(n),
        options=[{"label": "{}".format(i), "value": i} for i in range(1,11)],
        value=4,
      ),
      dbc.InputGroupAddon("SV", addon_type="prepend"),
      dbc.Select(
        id='save_{}'.format(n),
        options=[{"label": "{}+".format(i), "value": i} for i in range(1,8)],
        value=4,
      ),
      dbc.InputGroupAddon("INV", addon_type="prepend"),
      dbc.Select(
        id='invuln_{}'.format(n),
        options=[{"label": "{}++".format(i), "value": i} for i in range(1,8)],
        value=7,
      ),
      dbc.InputGroupAddon("FNP", addon_type="prepend"),
      dbc.Select(
        id='fnp_{}'.format(n),
        options=[{"label": "{}+++".format(i), "value": i} for i in range(1,8)],
        value=7,
      ),
      dbc.InputGroupAddon("W", addon_type="prepend"),
      dbc.Select(
        id='wounds_{}'.format(n),
        options=[{"label": "{}".format(i), "value": i} for i in range(1,24)],
        value=7,
      ),
    ],
    className="mb-2",
  )

def damage_input(n):
  # dropdown_menu_items = [dbc.DropdownMenuItem("Apply to all", 'apply_attack_{}'.format(n))]
  return dbc.InputGroup(
    [
      # dbc.DropdownMenu(dropdown_menu_items, label="Attack", addon_type="prepend"),
      dbc.InputGroupAddon("Attack", addon_type="prepend"),
      dbc.InputGroupAddon("WS", addon_type="prepend"),
      dbc.Select(
        id='ws_{}'.format(n),
        options=[{"label": "{}+".format(i), "value": i} for i in range(1,8)],
        value=4,
      ),
      dbc.InputGroupAddon("S", addon_type="prepend"),
      dbc.Select(
        id='strength_{}'.format(n),
        options=[{"label": "{}".format(i), "value": i} for i in range(1,21)],
        value=4,
      ),
      dbc.InputGroupAddon("AP", addon_type="prepend"),
      dbc.Select(
        id='ap_{}'.format(n),
        options=[{"label": "{}".format(i), "value": i} for i in range(0,7)],
        value=1,
      ),
      dbc.InputGroupAddon("Shots", addon_type="prepend"),
      dbc.Input(
        type="text",
        id='shots_{}'.format(n),
        value='2d6',
        style={'text-align': 'right'},
      ),
      dbc.InputGroupAddon("Damage", addon_type="prepend"),
      dbc.Input(
        type="text",
        id='damage_{}'.format(n),
        value='2',
        style={'text-align': 'right'}
      ),
    ],
    className="mb-2",
  )

def modify_shot_input(n):
  return dcc.Dropdown(
    persistence=True,
    id='shot_mods_{}'.format(n),
    multi=True,
    placeholder='Modify shot # rolls',
    className="mb-2",
  )

def modify_hit_input(n):
  return dcc.Dropdown(
    persistence=True,
    id='hit_mods_{}'.format(n),
    multi=True,
    placeholder='Modify hit rolls',
  )

def modify_wound_input(n):
  return dcc.Dropdown(
    persistence=True,
    id='wound_mods_{}'.format(n),
    multi=True,
    placeholder='Modify wound rolls',
  )

def modify_save_input(n):
  return dcc.Dropdown(
    persistence=True,
    id='save_mods_{}'.format(n),
    multi=True,
    placeholder='Modify save rolls',
  )

def modify_damage_input(n):
  return dcc.Dropdown(
    persistence=True,
    id='damage_mods_{}'.format(n),
    multi=True,
    placeholder='Modify damage rolls',
  )

def _text_input(input_id, value):
  return dbc.Input(persistence=True, id=input_id, value=value, type='text', style={'width': '100%'})

def _multi_input(input_id):
  return dcc.Dropdown(persistence=True, id=input_id, multi=True)

def _make_form_group(label, input):
  return dbc.FormGroup([dbc.Label(label),dbc.Col(input)])

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
  form_input = [
    tab_disable_input(n),
    attack_input(n),
    damage_input(n),
    dbc.Row([
      dbc.Col(modify_shot_input(n)),
      dbc.Col(modify_hit_input(n)),
      dbc.Col(modify_wound_input(n)),
    ]),
    dbc.Row([
      dbc.Col(modify_save_input(n)),
      dbc.Col(modify_damage_input(n)),
    ]),
  ]

  return dbc.Card(dbc.CardBody(form_input))


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
''')


def footer():
  return dcc.Markdown('''
### Also:
For the shots and damage characteristic, you can either use a fixed number or
XdY notation to represent a rolling
X dice with Y sides. You can also add modifiers to the hit and wound rolls that stack
(e.g. re-rolling 1's to hit and -1 to hit).
You can also download an image of the graph by clicking the camera icon
while hovering over the graph.

##### Updates:
* Removed the +/- 2 and 3 modifiers and instead you can now add +/-1 multiple times.
* Added the 'exploding dice' mechanic for hit rolls. You can stack them so for
example two "+1 hit on 6+" will yield +2 hits on a 6+.
* Added mortal wound generation for hit and wound rolls
* Added Haywire

This is still very much a work in progress, and there are probably still some bugs.
I'm /u/Uily on Reddit, so please let me know if you find any.
If you want to contribute
[you can find the repo here](https://github.com/akabbeke/WarhammerStatsEngine).

##### Todo:
* Figure out feed-forward abilities like rend
* Replace the frontend with an actual frontend instead of this cobbled
together dash frontend
* Figure out a way to allow users to create units and have all their weapons output
combined (Which russ is the best russ?)
* ???


There are no **Ads** funding this, so please don't be a dick. Otherwise,
I hope you find this useful!
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
    figure=graph_figure_template([{}] * tab_count),
    # style={"width" : "80%"},
  )

def settings_tabs(tab_count):

  tabs = []
  for i in range(1, tab_count+1):
    tabs.append(dbc.Tab(tab_settings(i), id='tab_{}'.format(i)))
  return dbc.Tabs(
    tabs,
    style={
      'padding-top': '4px',
      'padding-bottom': '4px',
    }
  )

def app_layout(tab_count):

  return html.Div([
    dbc.Row(dbc.Col(header())),
    dbc.Row(dbc.Col(damage_graph(tab_count)), className="m-2"),
    dbc.Row(dbc.Col(settings_tabs(tab_count))),
    dbc.Row(dbc.Col(footer())),
  ])