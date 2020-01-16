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
    return html.Div([
      dcc.Location(id='url'),
      html.Div(id='page-content')
    ])

  def base_layout(self):
    return html.Div(
      [
        self.navbar(),
        dbc.Select(),
        self.base_title(),
        dbc.Row(
          dbc.Col(
            GraphLayout(self.tab_count).layout(),
            className='portlet-container portlet-dropzone',
          ),
          style={'align-items': 'center'},
          className='flex-fill fill d-flex justify-content-start',
        ),
        dbc.Row(
          [
            dbc.Col(
              InputLayout(self.tab_count).layout(),
            ),
          ]
        ),
      ],
      className='container-fluid d-flex flex-column',
    )

  def base_title(self):
    content = dbc.InputGroup(
      [
        dbc.InputGroupAddon("Title", addon_type="prepend"),
        dbc.Input(
          type="text",
          id='title',
          value='',
          debounce=True,
          minLength=2,
          persistence=True,
          persistence_type='session',
          maxLength=140,
        ),
      ],
    )
    return dbc.CardBody(dbc.Row([dbc.Col(content)], className="mb-2 ",))

  def static_layout(self):
    return html.Div(
      [
        self.static_navbar(),
        html.Div(id='page-2-content',style={'display': 'none'}),
        dcc.RadioItems(
          id='page-2-radios',
          options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
          value='Orange',
          style={'display': 'none'}
        ),
        dbc.Row(
          dbc.Col(
            GraphLayout(self.tab_count).static_layout(),
            className='portlet-container portlet-dropzone',
          ),
          style={'align-items': 'center'},
          className='flex-fill fill d-flex justify-content-start',
        ),
      ],
      className='container-fluid d-flex flex-column',
    )

  def navbar(self):
    return dbc.NavbarSimple(
      children=[
        dbc.NavItem(
          dbc.NavLink(
            "permalink to this graph",
            id='permalink',
            href="https://github.com/akabbeke/WarhammerStatsEngine"
          )
        ),
      ],
      brand="Warhammer-Stats-Engine",
      brand_href="/",
      color="primary",
      dark=True,
    )

  def static_navbar(self):
    return dbc.NavbarSimple(
      children=[
        dbc.NavItem(
          dbc.NavLink(
            "Create your own graph",
            id='permalink',
            href="/"
          )
        ),
      ],
      brand="Warhammer-Stats-Engine",
      brand_href="/",
      color="primary",
      dark=True,
    )

app_color = {"graph_bg": "#082255", "graph_line": "#a3a7b0"}

class GraphLayout(object):
  def __init__(self, tab_count=0):
    self.tab_count = tab_count

  def layout(self):
    content = dcc.Graph(
      id='damage_graph',
      style={'height':'60vh'},
      figure=self.figure_template(),
      config={
        'scrollZoom': False,
        'displayModeBar': False,
      },

    )
    return content

  def static_layout(self):
    content = dcc.Graph(
      id='static_damage_graph',
      style={'height':'75vh'},
      figure=self.figure_template(),
      config={
        'scrollZoom': False,
        # 'displayModeBar': False,
      },

    )
    return content

  def figure_template(self, data=None, max_len=10, title=None):
    return {
      'data': data or [{}] * self.tab_count,
      'layout': {
        'title': title,
        'showlegend': True,
        'legend': dict(orientation='h',yanchor='top',xanchor='center',y=1, x=0.5),
        # 'template': 'plotly_dark',
        'xaxis': {
            'title': 'Minimum Wounds Dealt to Target',
            'type': 'linear',
            'range': [0, max_len],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 1,
            "gridcolor": app_color["graph_line"],
            "color": app_color["graph_line"],
            'fixedrange': True,
        },
        'yaxis': {
            'title': 'Probability of Minimum Wounds Dealt',
            'type': 'linear',
            'range': [0, 100],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 10,
            "gridcolor": app_color["graph_line"],
            "color": app_color["graph_line"],
            'fixedrange': True,
        },
        'margin':{
          'l': 70,
          'r': 70,
          'b': 50,
          't': 50,
          'pad': 4,
        },
        'autosize': True,
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'paper_bgcolor': 'rgba(0,0,0,0)',
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
      *self.mod_rows(tab_index),
    ]
    return dbc.CardBody(form_input)

  def data_row_input(self, tab_index):
    content = [
      dbc.InputGroupAddon("Enable", addon_type="prepend"),
      dbc.InputGroupAddon(
        dbc.Checkbox(checked=tab_index==0, id='enabled_{}'.format(tab_index)),
        id=f'enabled_addon{tab_index}',
        addon_type="prepend",
      ),
      dbc.Tooltip(
        f"Enable this tab",
        target=f'enabled_addon{tab_index}',
      ),
      dbc.Input(
        type="text",
        id='tab_name_{}'.format(tab_index),
        value='Profile {}'.format(tab_index),
        debounce=True,
        minLength=2,
        persistence=True,
        persistence_type='session',
        maxLength=60
      ),
      dbc.Tooltip(
        f"Name this tab",
        target=f'tab_name_{tab_index}',
      ),
      dbc.InputGroupAddon("Average", addon_type="prepend", id='avg_display_{}'.format(tab_index)),
      dbc.Tooltip(
        f"The mean value of the damage distribution",
        target=f'avg_display_{tab_index}',
      ),
      dbc.InputGroupAddon("σ", addon_type="apend", id='std_display_{}'.format(tab_index)),
      dbc.Tooltip(
        f"The standard deviation of the distribution",
        target=f'std_display_{tab_index}',
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
      dbc.InputGroupAddon("T", id=f'toughness_addon_{tab_index}', addon_type="prepend"),
      dbc.Select(
        id='toughness_{}'.format(tab_index),
        options=[{"label": "{}".format(i), "value": i} for i in range(1,11)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        f"Set the toughness of the target",
        target=f'toughness_addon_{tab_index}',
      ),
    ]

  def _save_input(self, tab_index):
    return [
      dbc.InputGroupAddon("SV", id=f'save_addon_{tab_index}', addon_type="prepend"),
      dbc.Select(
        id='save_{}'.format(tab_index),
        options=[{"label": "{}+".format(i), "value": i} for i in range(2,8)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        f"Set the save value of the target",
        target=f'save_addon_{tab_index}',
      ),
    ]

  def _invuln_input(self, tab_index):
    return [
      dbc.InputGroupAddon("INV", id=f'invuln_addon_{tab_index}', addon_type="prepend"),
      dbc.Select(
        id='invuln_{}'.format(tab_index),
        options=[{"label": "{}++".format(i), "value": i} for i in range(2,8)],
        value=7,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        f"Set the invulnerable save value of the target",
        target=f'invuln_addon_{tab_index}',
      ),
    ]

  def _fnp_input(self, tab_index):
    return [
      dbc.InputGroupAddon("FNP", id=f'fnp_addon_{tab_index}', addon_type="prepend"),
      dbc.Select(
        id='fnp_{}'.format(tab_index),
        options=[{"label": "{}+++".format(i), "value": i} for i in range(2,8)],
        value=7,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        f"Set the feel no pain value of the target",
        target=f'fnp_addon_{tab_index}',
      ),
    ]

  def _wounds_input(self, tab_index):
    return [
      dbc.InputGroupAddon("W", id=f'wounds_addon_{tab_index}', addon_type="prepend"),
      dbc.Select(
        id='wounds_{}'.format(tab_index),
        options=[{"label": "{}".format(i), "value": i} for i in range(1,25)],
        value=7,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        f"Set the target wounds value",
        target=f'wounds_addon_{tab_index}',
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
      dbc.InputGroupAddon("WS", id=f'ws_addon_{tab_index}', addon_type="prepend"),
      dbc.Select(
        id='ws_{}'.format(tab_index),
        options=[{"label": "{}+".format(i), "value": i} for i in range(1,8)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        f"Set the weapons skill value",
        target=f'ws_addon_{tab_index}',
      ),
    ]

  def _strength_input(self, tab_index):
    return [
      dbc.InputGroupAddon("S", id=f'strength_addon_{tab_index}', addon_type="prepend"),
      dbc.Select(
        id='strength_{}'.format(tab_index),
        options=[{"label": "{}".format(i), "value": i} for i in range(1,21)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        f"Set the strength value",
        target=f'strength_addon_{tab_index}',
      ),
    ]

  def _ap_input(self, tab_index):
    return [
      dbc.InputGroupAddon("AP", id=f'ap_addon_{tab_index}', addon_type="prepend"),
      dbc.Select(
        id='ap_{}'.format(tab_index),
        options=[{"label": "0" if i==0 else "-{}".format(i), "value": i} for i in range(0,7)],
        value=1,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        f"Set the AP value",
        target=f'ap_addon_{tab_index}',
      ),
    ]

  def _shots_input(self, tab_index):
    return [
      dbc.InputGroupAddon("#", id=f'shots_addon_{tab_index}', addon_type="prepend"),
      dbc.Input(
        type="text",
        id=f'shots_{tab_index}',
        value='2d6',
        style={'text-align': 'right'},
        persistence=True,
        persistence_type='session',
        debounce=True,
        pattern=r'^(\d+)?[dD]?(\d+)$',
      ),
      dbc.Tooltip(
        f"Set the number of shots (1, 2d6, d3, ...)",
        target=f'shots_addon_{tab_index}',
      ),
    ]

  def _damage_input(self, tab_index):
    return [
      dbc.InputGroupAddon("D", id=f'damage_addon_{tab_index}', addon_type="prepend"),
      dbc.Input(
        type="text",
        id='damage_{}'.format(tab_index),
        value='2',
        style={'text-align': 'right'},
        persistence=True,
        persistence_type='session',
        debounce=True,
        pattern=r'^(\d+)?[dD]?(\d+)$',
      ),
      dbc.Tooltip(
        f"Set the damage dealt (1, 2d6, d3, ...)",
        target=f'damage_addon_{tab_index}',
      ),
    ]

  def mod_rows(self, tab_index):
    shot_modifier = dcc.Dropdown(
      options=self._shot_modifier_options(),
      multi=True,
      placeholder='Modify shot volume rolls',
      optionHeight=20,
      id=f'shot_mods_{tab_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    hit_modifier = dcc.Dropdown(
      options=self._hit_modifier_options(),
      multi=True,
      placeholder='Modify hit rolls',
      optionHeight=20,
      id=f'hit_mods_{tab_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    wound_modifier = dcc.Dropdown(
      options=self._wound_modifier_options(),
      multi=True,
      placeholder='Modify wound rolls',
      optionHeight=20,
      id=f'wound_mods_{tab_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    save_modifier = dcc.Dropdown(
      options=self._save_modifier_options(),
      multi=True,
      placeholder='Modify save rolls',
      optionHeight=20,
      id=f'save_mods_{tab_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    damage_modifier = dcc.Dropdown(
      options=self._damage_modifier_options(),
      multi=True,
      placeholder='Modify damage rolls',
      optionHeight=20,
      id=f'damage_mods_{tab_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    return [
      dbc.Row(dbc.Col(shot_modifier), className="mb-2 "),
      dbc.Row(dbc.Col(hit_modifier), className="mb-2 "),
      dbc.Row(dbc.Col(wound_modifier), className="mb-2 "),
      dbc.Row(dbc.Col(save_modifier), className="mb-2 "),
      dbc.Row(dbc.Col(damage_modifier), className="mb-2 "),
    ]

  def _shot_modifier_options(self):
    options = [
      {'label': f'Reroll all dice', 'value': f'reroll_allvol'},
      {'label': f'Reroll one dice', 'value': f'reroll_one_dicevol'},
      {'label': f'Reroll ones', 'value': f'reroll_ones'},
      {'label': f'Roll two dice choose highest', 'value': f'reroll_melta'},
      {'label': f'Add +D6', 'value': f'addvol_d6'},
      {'label': f'Add +D3', 'value': f'addvol_d3'},
    ]
    for i in range(1, 7):
      options.append({'label': f'Add +{i}', 'value': f'add_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i}', 'value': f'sub_{i}'})
    return options

  def _hit_modifier_options(self):
    options = [
      {'label': f'Reroll all dice', 'value': f'reroll_all'},
      {'label': f'Reroll failed dice', 'value': f'reroll_failed'},
      {'label': f'Reroll one dice', 'value': f'reroll_one_dice'},
      {'label': f'Reroll ones', 'value': f'reroll_ones'},
    ]
    for i in range(1, 7):
      options.append({'label': f'Add +{i}', 'value': f'add_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i}', 'value': f'sub_{i}'})
    for x in ['MW', 'hit', 'shot']:
      for i in range(1, 7):
        for j in range(2, 7):
          options.append({'label': f'+{i} {x} on a {j}+', 'value': f'addon_{i}_{x}_{j}_mod'})
    for x in ['MW', 'hit', 'shot']:
      for i in range(1, 7):
        for j in range(2, 7):
          values = ', '.join([str(x) for x in range(j, 7)])
          options.append({'label': f'+{i} {x} on a {values}', 'value': f'addon_{i}_{x}_{j}'})
    return options

  def _wound_modifier_options(self):
    options = [
      {'label': f'Reroll all dice', 'value': f'reroll_all'},
      {'label': f'Reroll failed dice', 'value': f'reroll_failed'},
      {'label': f'Reroll one dice', 'value': f'reroll_one_dice'},
      {'label': f'Reroll ones', 'value': f'reroll_ones'},
      {'label': f'Haywire', 'value': f'haywire'},
    ]
    for i in range(1, 7):
      options.append({'label': f'Add +{i}', 'value': f'add_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i}', 'value': f'sub_{i}'})
    # for i in range(2, 7):
    #   options.append({'label': f'Only wound on {i}+', 'value': f'lower_{i}'})
    for i in range(1, 7):
      for j in range(2, 7):
        options.append({'label': f'+{i} MW on a {j}+', 'value': f'addon_{i}_MW_{j}_mod'})
    for i in range(1, 7):
      for j in range(2, 7):
        values = ', '.join([str(x) for x in range(j, 7)])
        options.append({'label': f'+{i} MW on a {values}', 'value': f'addon_{i}_MW_{j}'})
    return options

  def _save_modifier_options(self):
    options = [
      {'label': f'Reroll all dice', 'value': f'reroll_all'},
      {'label': f'Reroll failed dice', 'value': f'reroll_failed'},
      {'label': f'Reroll one dice', 'value': f'reroll_one_dice'},
      {'label': f'Reroll ones', 'value': f'reroll_ones'},
      {'label': f'Ignore invulnerable', 'value': f'ignoreinv'},
    ]
    for i in range(1, 7):
      options.append({'label': f'Add +{i} to save', 'value': f'saveadd_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i} to save', 'value': f'savesub_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Add +{i} to invuln', 'value': f'invadd_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i} to invuln', 'value': f'invsub_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Ignore AP -{i} and lower', 'value': f'ignoreap_{i}'})
    return options

  def _damage_modifier_options(self):
    options = [
      {'label': f'Reroll all dice', 'value': f'reroll_allvol'},
      {'label': f'Reroll one dice', 'value': f'reroll_one_dicevol'},
      {'label': f'Reroll ones', 'value': f'reroll_ones'},
      {'label': f'Roll two dice choose highest', 'value': f'reroll_melta'},
      {'label': f'Half damage (rounding up)', 'value': f'halfdam'},
    ]
    for i in range(1, 7):
      options.append({'label': f'Add +{i}', 'value': f'add_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i}', 'value': f'sub_{i}'})
    for i in range(2, 7):
      options.append({'label': f'Minimum {i} damage', 'value': f'minval_{i}'})
    return options


class InputGenerator(object):
  def gen_tab_inputs(self, tab_index):
    return {
      **self.data_row_input(tab_index),
      **self.target_row_input(tab_index),
      **self.attack_row_input(tab_index),
      **self.modify_input(tab_index),
    }

  def json_inputs(self, tab_count):
    json_input = []
    for i in range(tab_count):
      json_input += self.json_tab_inputs(i)
    return json_input

  def json_tab_inputs(self, tab_index):
    return [
      f'shot_mods_{tab_index}'
      f'hit_mods_{tab_index}'
      f'wound_mods_{tab_index}'
      f'save_mods_{tab_index}'
      f'damage_mods_{tab_index}'
    ]

  def data_row_input(self, tab_index):
    return {
      f'enabled_{tab_index}': 'checked',
      f'tab_name_{tab_index}': 'value',
    }

  def target_row_input(self, tab_index):
    return {
      f'toughness_{tab_index}': 'value',
      f'save_{tab_index}': 'value',
      f'invuln_{tab_index}': 'value',
      f'fnp_{tab_index}': 'value',
      f'wounds_{tab_index}': 'value',
    }

  def attack_row_input(self, tab_index):
    return {
      f'ws_{tab_index}': 'value',
      f'strength_{tab_index}': 'value',
      f'ap_{tab_index}': 'value',
      f'shots_{tab_index}': 'value',
      f'damage_{tab_index}': 'value',
    }

  def modify_input(self, tab_index):
    return {
      f'shot_mods_{tab_index}': 'value',
      f'hit_mods_{tab_index}': 'value',
      f'wound_mods_{tab_index}': 'value',
      f'save_mods_{tab_index}': 'value',
      f'damage_mods_{tab_index}': 'value',
    }

  def graph_inputs(self, tab_count):
    inputs = {'title': 'value'}
    for i in range(tab_count):
      inputs.update(self.gen_tab_inputs(i))
    return inputs

def app_layout(tab_count):
  return Layout(tab_count).layout()
