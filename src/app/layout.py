import dash
import dash_daq
import re
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc



FOOTER_CONTENT = '''

This is still very much a work in progress, and there are probably still some bugs.
I'm [/u/Uily](https://www.reddit.com/user/uily) on Reddit, so please let me know if
you find any. Checkout the code for this project here: https://github.com/akabbeke/WarhammerStatsEngine

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

##### Todo:
* Figure out feed-forward abilities like rend
* Replace the frontend with an actual frontend instead of this cobbled
together dash frontend
* Figure out a way to allow users to create units and have all their weapons output
combined (Which russ is the best russ?)
* ???


There are no **Ads** funding this, so please don't be a dick. Otherwise,
I hope you find this useful!
'''

class Layout(object):
  def __init__(self, tab_count=0):
    self.tab_count = tab_count

  def layout(self):
    return html.Div(
      [
        dbc.Row(
          dbc.Col(
            GraphLayout(self.tab_count).layout(),
            className='portlet-container portlet-dropzone',
          ),
          style={'align-items': 'center'},
          className='flex-fill fill d-flex justify-content-start',
        ),
        dbc.Row(
          dbc.Col(
            InputLayout(self.tab_count).layout(),
          ),
        ),
      ],
      className='container-fluid d-flex vh-100 flex-column',
    )


class GraphLayout(object):
  def __init__(self, tab_count=0):
    self.tab_count = tab_count

  def layout(self):
    content = dcc.Graph(
      id='damage-graph',
      figure=self.figure_template(),
      style={'height':'60vh'}
    )
    return content

  def figure_template(self, data=None, max_len=24):
    return {
      'data': data or [{}] * self.tab_count,
      'layout': {
        'showlegend': True,
        'legend': dict(orientation='h',yanchor='top',xanchor='center',y=1.05, x=0.5),
        'xaxis': {
            'title': 'Minimum Wounds Dealt to Target',
            'type': 'linear',
            'range': [0, max_len],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 1,
            'fixedrange': True,
        },
        'yaxis': {
            'title': 'Probability of Minimum Wounds Dealt',
            'type': 'linear',
            'range': [0, 100],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 10,
            'fixedrange': True,
        },
        'title': 'A Fancy Plot',
        'autosize': True,
        'title': 'warhammer-stats-engine.com'
      },
    }


class InputLayout(object):
  def __init__(self, tab_count=0):
    self.tab_count = tab_count

  def layout(self):
    tabs = []
    for i in range(self.tab_count):
      tab = dbc.Tab(
        self.tab_content(i),
        id='tab_{}'.format(i),
        label='Profile {}'.format(i + 1),
        style={'width': '100%'},
      )
      tabs.append(tab)
    tabs.append(
      dbc.Tab(
        dbc.CardBody(self.footer()),

        label='Info Tab',
        style={'width': '100%'},
      )
    )
    return dbc.Tabs(
      tabs,
      className='nav-justified',
      style={'padding-top': '4px', 'padding-bottom': '4px'},
    )

  def footer(self):
    return dcc.Markdown(FOOTER_CONTENT)

  def tab_content(self, tab_index):
    form_input = [
      self.data_row_input(tab_index),
      self.attack_row_input(tab_index),
      self.target_row_input(tab_index),
      *self.modify_input(tab_index),
    ]
    return dbc.CardBody(form_input)

  def data_row_input(self, tab_index):
    content = [
      dbc.InputGroupAddon("Enable", addon_type="prepend"),
      dbc.InputGroupAddon(dbc.Checkbox(checked=tab_index==0, id='enabled_{}'.format(tab_index)), addon_type="prepend"),
      dbc.Input(
        type="text",
        id='tab_name_{}'.format(tab_index),
        value='Profile {}'.format(tab_index),
        debounce=True,
        minLength=2,
        persistence=True,
      ),
    ]
    return dbc.Row(
      [dbc.Col(dbc.InputGroup(content))],
      className="mb-2 ",
    )

  def target_row_input(self, tab_index):
    content = dbc.InputGroup(
      [
        dbc.InputGroupAddon("Target", addon_type="prepend"),
        *self._toughness_input(tab_index),
        *self._save_input(tab_index),
        *self._invuln_input(tab_index),
        *self._fnp_input(tab_index),
        *self._wounds_input(tab_index),
      ],
    )
    return dbc.Row([dbc.Col(content)], className="mb-2 ",)

  def _toughness_input(self, tab_index):
    return [
      dbc.InputGroupAddon("T", addon_type="prepend"),
      dbc.Select(
        id='toughness_{}'.format(tab_index),
        options=[{"label": "{}".format(i), "value": i} for i in range(1,11)],
        value=4,
        persistence=True,
      ),
    ]

  def _save_input(self, tab_index):
    return [
      dbc.InputGroupAddon("SV", addon_type="prepend"),
      dbc.Select(
        id='save_{}'.format(tab_index),
        options=[{"label": "{}+".format(i), "value": i} for i in range(2,8)],
        value=4,
        persistence=True,
      ),
    ]

  def _invuln_input(self, tab_index):
    return [
      dbc.InputGroupAddon("INV", addon_type="prepend"),
      dbc.Select(
        id='invuln_{}'.format(tab_index),
        options=[{"label": "{}++".format(i), "value": i} for i in range(2,8)],
        value=7,
        persistence=True,
      ),
    ]

  def _fnp_input(self, tab_index):
    return [
      dbc.InputGroupAddon("FNP", addon_type="prepend"),
      dbc.Select(
        id='fnp_{}'.format(tab_index),
        options=[{"label": "{}+++".format(i), "value": i} for i in range(2,8)],
        value=7,
        persistence=True,
      ),
    ]

  def _wounds_input(self, tab_index):
    return [
      dbc.InputGroupAddon("W", addon_type="prepend"),
      dbc.Select(
        id='wounds_{}'.format(tab_index),
        options=[{"label": "{}".format(i), "value": i} for i in range(1,25)],
        value=7,
        persistence=True,
      ),
    ]

  def attack_row_input(self, tab_index):
    content = dbc.InputGroup(
      [
        dbc.InputGroupAddon("Attack", addon_type="prepend"),
        *self._strength_input(tab_index),
        *self._ap_input(tab_index),
        *self._weapon_skill_input(tab_index),
        *self._shots_input(tab_index),
        *self._damage_input(tab_index),
      ],
    )
    return dbc.Row([dbc.Col(content)], className="mb-2 ",)

  def _weapon_skill_input(self, tab_index):
    return [
      dbc.InputGroupAddon("WS", addon_type="prepend"),
      dbc.Select(
        id='ws_{}'.format(tab_index),
        options=[{"label": "{}+".format(i), "value": i} for i in range(1,8)],
        value=4,
        persistence=True,
      ),
    ]

  def _strength_input(self, tab_index):
    return [
      dbc.InputGroupAddon("S", addon_type="prepend"),
      dbc.Select(
        id='strength_{}'.format(tab_index),
        options=[{"label": "{}".format(i), "value": i} for i in range(1,21)],
        value=4,
        persistence=True,
      ),
    ]

  def _ap_input(self, tab_index):
    return [
      dbc.InputGroupAddon("AP", addon_type="prepend"),
      dbc.Select(
        id='ap_{}'.format(tab_index),
        options=[{"label": "0" if i==0 else "-{}".format(i), "value": i} for i in range(0,7)],
        value=1,
        persistence=True,
      ),
    ]

  def _shots_input(self, tab_index):
    return [
      dbc.InputGroupAddon("Shots", addon_type="prepend"),
      dbc.Input(
        type="text",
        id='shots_{}'.format(tab_index),
        value='2d6',
        style={'text-align': 'right'},
        persistence=True,
      ),
    ]

  def _damage_input(self, tab_index):
    return [
      dbc.InputGroupAddon("Damage", addon_type="prepend"),
      dbc.Input(
        type="text",
        id='damage_{}'.format(tab_index),
        value='2',
        style={'text-align': 'right'},
        persistence=True,
      ),
    ]

  def modify_input(self, tab_index):
    return [
      dbc.Row([
        dbc.Col(self._modify_shot_input(tab_index)),
        dbc.Col(self._modify_hit_input(tab_index)),
        dbc.Col(self._modify_wound_input(tab_index)),
      ], className="",),
      dbc.Row([
        dbc.Col(self._modify_save_input(tab_index)),
        dbc.Col(self._modify_damage_input(tab_index)),
      ], className="mb-0 ",),
    ]

  def _modify_shot_input(self, tab_index):
    return dcc.Dropdown(
      persistence=True,
      id='shot_mods_{}'.format(tab_index),
      multi=True,
      placeholder='Modify shot # rolls',
      className="mb-2 ",
    )

  def _modify_hit_input(self, tab_index):
    return dcc.Dropdown(
      persistence=True,
      id='hit_mods_{}'.format(tab_index),
      multi=True,
      placeholder='Modify hit rolls',
    )

  def _modify_wound_input(self, tab_index):
    return dcc.Dropdown(
      persistence=True,
      id='wound_mods_{}'.format(tab_index),
      multi=True,
      placeholder='Modify wound rolls',
    )

  def _modify_save_input(self, tab_index):
    return dcc.Dropdown(
      persistence=True,
      id='save_mods_{}'.format(tab_index),
      multi=True,
      placeholder='Modify save rolls',
    )

  def _modify_damage_input(self, tab_index):
    return dcc.Dropdown(
      persistence=True,
      id='damage_mods_{}'.format(tab_index),
      multi=True,
      placeholder='Modify damage rolls',
    )


class MultiOptionGenerator(object):
  def shot_options(self, selected):
    base_options = [
      ['re_roll_1s', 'Re-roll 1\'s', 1],
      ['re_roll_dice', 'Re-roll all rolls', 1],
    ]
    return self._generate_options(base_options, selected)

  def hit_options(self, selected):
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
    return self._generate_options(base_options, selected)

  def wound_options(self, selected):
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
    return self._generate_options(base_options, selected)

  def save_options(self, selected):
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
    return self._generate_options(base_options, selected)

  def damage_options(self, selected):
    base_options = [
      ['re_roll_1s', 'Re-roll 1\'s', 1],
      ['re_roll_dice', 'Re-roll all rolls', 1],
      ['minimum_3', 'Minimum 3', 1],
      ['melta', 'Melta', 1],
      ['half_damage', 'Half Damage', 1],
      ['add_1', 'Add +1', 4],
      ['sub_1', 'Sub -1', 5],
    ]
    return self._generate_options(base_options, selected)

  def _generate_options(self, base_options, selected):
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


class InputGenerator(object):
  def gen_tab_inputs(self, tab_index):
    return [
      *self.data_row_input(tab_index),
      *self.target_row_input(tab_index),
      *self.attack_row_input(tab_index),
      *self.modify_input(tab_index),
    ]

  def data_row_input(self, tab_index):
    return [
      'enabled_{}'.format(tab_index),
      'tab_name_{}'.format(tab_index)
    ]

  def target_row_input(self, tab_index):
    return [
      'toughness_{}'.format(tab_index),
      'save_{}'.format(tab_index),
      'invuln_{}'.format(tab_index),
      'fnp_{}'.format(tab_index),
      'wounds_{}'.format(tab_index),
    ]

  def attack_row_input(self, tab_index):
    return [
      'ws_{}'.format(tab_index),
      'strength_{}'.format(tab_index),
      'ap_{}'.format(tab_index),
      'shots_{}'.format(tab_index),
      'damage_{}'.format(tab_index),
    ]

  def modify_input(self, tab_index):
    return [
      'shot_mods_{}'.format(tab_index),
      'hit_mods_{}'.format(tab_index),
      'wound_mods_{}'.format(tab_index),
      'save_mods_{}'.format(tab_index),
      'damage_mods_{}'.format(tab_index),
    ]

  def graph_inputs(self, tab_count):
    inputs = []
    for i in range(tab_count):
      inputs += self.gen_tab_inputs(i)
    return inputs

def app_layout(tab_count):
  return Layout(tab_count).layout()
