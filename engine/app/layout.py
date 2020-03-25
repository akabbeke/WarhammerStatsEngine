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
* ???

There are no **ads** funding this, so please don't be a dick. Otherwise,
I hope you find this useful!
'''

class Layout(object):
  def __init__(self, tab_count=0, weapon_count=0):
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def layout(self):
    return html.Div([
      dcc.Location(id='url'),
      html.Div(id='page_content')
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
              InputLayout(self.tab_count, self.weapon_count).layout(),
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
        html.Div(id='static_graph_debug', style={'display': 'none'}),
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
            href="https://github.com/akabbeke/WarhammerStatsEngine",
            external_link=True,
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
        'toImageButtonOptions': {
          'format': 'jpeg',
          'filename': 'warhammer_plot',
          'height': 1080,
          'width': 1920,
          'scale': 1
        },
        # 'displayModeBar': False,
      },

    )
    return content

  def static_layout(self):
    content = dcc.Graph(
      id='static_damage_graph',
      style={'height':'85vh'},
      figure=self.figure_template(),
      config={
        'scrollZoom': False,
        'toImageButtonOptions': {
          'format': 'jpeg',
          'filename': 'warhammer_plot',
          'height': 1080,
          'width': 1920,
          'scale': 1
        },
        # 'displayModeBar': False,
      },

    )
    return content

  def figure_template(self, data=None, max_len=10, title=None, static=False):
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
      },
    }


class InputLayout(object):
  def __init__(self, tab_count=0, weapon_count=0):
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def layout(self):
    tabs = []
    for i in range(self.tab_count):
      tab = InputTabLayout(i, self.tab_count, self.weapon_count).layout()
      tabs.append(tab)
    tabs.append(
      dbc.Tab(
        dbc.CardBody(dcc.Markdown(FOOTER_CONTENT)),
        label='Info Tab',
        style={'width': '100%'},
      )
    )
    return dbc.Tabs(
      tabs,
      className='nav-justified',
      style={'padding-top': '4px', 'padding-bottom': '0px'},
    )


class InputTabLayout(object):
  def __init__(self, tab_index, tab_count=0, weapon_count=0):
    self.tab_index = tab_index
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def layout(self):
    return dbc.Tab(
      self.tab_content(),
      id='tab_{}'.format(self.tab_index),
      label='Profile {}'.format(self.tab_index + 1),
      style={'width': '100%'},
    )

  def tab_content(self):
    form_input = [
      self._data_input_row(),
      self._target_input_row(),
      self._weapon_tabs(),
    ]
    return self._wrap_card(form_input)

  def _wrap_card(self, content):
    return dbc.Card(dbc.CardBody(content),className="mb-2 ")

  def _data_input_row(self):
    return dbc.Row(
      [
        dbc.Col(self._tab_enable_inout(), width=2),
        dbc.Col(self._tab_name_input()),
        dbc.Col(html.P("Average", id=f'avgdisplay_{self.tab_index}'), width=2),
        dbc.Col(html.P("σ", id=f'stddisplay_{self.tab_index}'), width=2),
      ],
      className='mb-2',
    )

  def _tab_enable_inout(self):
    content = [
      dbc.Select(
        options=[
          {"label": "Enabled", "value": 'enabled'},
          {"label": "Disabled", "value": 'disabled'}
        ],
        value='enabled' if self.tab_index == 0 else 'disabled',
        disabled=self.tab_index == 0,
        id=f'enabled_{self.tab_index}',
        persistence=True,
        persistence_type='session',
      )
    ]
    return dbc.InputGroup(content, size="sm")

  def _tab_name_input(self):
    content = [
      dbc.InputGroupAddon("Name", addon_type="prepend"),
      dbc.Input(
        type="text",
        id=f'tabname_{self.tab_index}',
        value=f'Profile {self.tab_index}',
        debounce=True,
        minLength=2,
        persistence=True,
        persistence_type='session',
        maxLength=60
      ),
    ]
    return dbc.InputGroup(content, size="sm")

  def _target_input_row(self):
    content = dbc.InputGroup(
      [
        dbc.InputGroupAddon("Target", addon_type="prepend"),
        *self._toughness_input(),
        *self._save_input(),
        *self._invuln_input(),
        *self._fnp_input(),
        *self._wounds_input(),
      ],
      size="sm",
    )
    return dbc.Row([dbc.Col(content)], className="mb-2 ",)

  def _toughness_input(self):
    return [
      dbc.InputGroupAddon('T', id=f'toughness_addon_{self.tab_index}', addon_type='prepend'),
      dbc.Select(
        id=f'toughness_{self.tab_index}',
        options=[{'label': f'{i}', 'value': i} for i in range(1,11)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the toughness of the target',
        target=f'toughness_addon_{self.tab_index}',
      ),
    ]

  def _save_input(self):
    return [
      dbc.InputGroupAddon('SV', id=f'save_addon_{self.tab_index}', addon_type='prepend'),
      dbc.Select(
        id=f'save_{self.tab_index}',
        options=[{'label': f'{i}+', 'value': i} for i in range(2,8)],
        value=3,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the save value of the target',
        target=f'save_addon_{self.tab_index}',
      ),
    ]

  def _invuln_input(self):
    return [
      dbc.InputGroupAddon('INV', id=f'invuln_addon_{self.tab_index}', addon_type='prepend'),
      dbc.Select(
        id=f'invuln_{self.tab_index}',
        options=[{'label': f'{i}++', 'value': i} for i in range(2,8)],
        value=7,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the invulnerable save value of the target',
        target=f'invuln_addon_{self.tab_index}',
      ),
    ]

  def _fnp_input(self):
    return [
      dbc.InputGroupAddon('FNP', id=f'fnp_addon_{self.tab_index}', addon_type='prepend'),
      dbc.Select(
        id=f'fnp_{self.tab_index}',
        options=[{'label': f'{i}+++', 'value': i} for i in range(2,8)],
        value=7,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the feel no pain value of the target',
        target=f'fnp_addon_{self.tab_index}',
      ),
    ]

  def _wounds_input(self):
    return [
      dbc.InputGroupAddon('W', id=f'wounds_addon_{self.tab_index}', addon_type='prepend'),
      dbc.Select(
        id=f'wounds_{self.tab_index}',
        options=[{'label': f'{i}', 'value': i} for i in range(1,25)],
        value=2,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the target wounds value',
        target=f'wounds_addon_{self.tab_index}',
      ),
    ]

  def _weapon_tabs(self):
    weapon_tabs = []
    for weapon_index in range(self.weapon_count):
      weapon_tab = WeaponTabLayout(
        self.tab_index,
        weapon_index,
        self.tab_count,
        self.weapon_count
      ).layout()
      weapon_tabs.append(weapon_tab)
    return dbc.Tabs(
      weapon_tabs,
      className='nav-justified',
      style={'padding-top': '0px', 'padding-bottom': '0px'},
    )


class WeaponTabLayout(object):
  def __init__(self, tab_index, weapon_index, tab_count=0, weapon_count=0):
    self.tab_index = tab_index
    self.weapon_index = weapon_index
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def layout(self):
    return dbc.Tab(
      self._tab_content(),
      id=f'weapontab_{self.tab_index}_{self.weapon_index}',
      label='Weapon {}'.format(self.weapon_index + 1),
      style={'width': '100%'}
    )

  def _tab_content(self):
    form_input = [
      self._weapon_name_row(),
      self._attack_input_row(),
      *self._modifier_rows()
    ]
    return self._wrap_card(form_input)

  def _wrap_card(self, content):
    return dbc.Card(dbc.CardBody(content))

  def _wrap_single_row(self, content):
    return dbc.Row([dbc.Col(content)], className="mb-2 ",)

  def _weapon_name_row(self):
    return dbc.Row(
      [
        dbc.Col(self._weapon_enable_input(), width=2),
        dbc.Col(self._weapon_name_input()),
      ],
      className='mb-2',
    )

  def _weapon_enable_input(self):
    return dbc.InputGroup([
      dbc.Select(
        options=[
          {'label': 'Enabled', 'value': 'enabled'},
          {'label': 'Disabled', 'value': 'disabled'}
        ],
        value='enabled' if self.weapon_index == 0 else 'disabled',
        disabled=self.weapon_index == 0,
        persistence=True,
        persistence_type='session',
        id=f'weaponenabled_{self.tab_index}_{self.weapon_index}',
      ),
    ], size="sm")

  def _weapon_name_input(self):
    return dbc.InputGroup([
      dbc.InputGroupAddon("Name", addon_type="prepend"),
      dbc.Input(
        type="text",
        id=f'weaponname_{self.tab_index}_{self.weapon_index}',
        value=f'Weapon {self.weapon_index+1}',
        debounce=True,
        minLength=2,
        persistence=True,
        persistence_type='session',
        maxLength=60
      ),
    ], size="sm")

  def _attack_input_row(self):
    content = [
      *self._strength_input(),
      *self._ap_input(),
      *self._weapon_skill_input(),
      *self._shots_input(),
      *self._damage_input(),
    ]

    return self._wrap_single_row(dbc.InputGroup(content, size="sm",))


  def _weapon_skill_input(self):
    return [
      dbc.InputGroupAddon(
        'WS',
        id=f'ws_addon_{self.tab_index}_{self.weapon_index}',
        addon_type='prepend'
      ),
      dbc.Select(
        id=f'ws_{self.tab_index}_{self.weapon_index}',
        options=[{'label': f'{i}+', 'value': i} for i in range(1,8)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the weapons skill value',
        target=f'ws_addon_{self.tab_index}_{self.weapon_index}',
      ),
    ]

  def _strength_input(self):
    return [
      dbc.InputGroupAddon(
        'S',
        id=f'strength_addon_{self.tab_index}_{self.weapon_index}',
        addon_type='prepend'
      ),
      dbc.Select(
        id=f'strength_{self.tab_index}_{self.weapon_index}',
        options=[{'label': f'{i}', 'value': i} for i in range(1,21)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the strength value',
        target=f'strength_addon_{self.tab_index}_{self.weapon_index}',
      ),
    ]

  def _ap_input(self):
    return [
      dbc.InputGroupAddon(
        'AP',
        id=f'ap_addon_{self.tab_index}_{self.weapon_index}',
        addon_type="prepend"
      ),
      dbc.Select(
        id=f'ap_{self.tab_index}_{self.weapon_index}',
        options=[{'label': '0' if i==0 else f'-{i}', 'value': i} for i in range(0,7)],
        value=1,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the AP value',
        target=f'ap_addon_{self.tab_index}_{self.weapon_index}',
      ),
    ]

  def _shots_input(self):
    return [
      dbc.InputGroupAddon(
        '#',
        id=f'shots_addon_{self.tab_index}_{self.weapon_index}',
        addon_type="prepend"
      ),
      dbc.Input(
        type='text',
        id=f'shots_{self.tab_index}_{self.weapon_index}',
        value='2d6',
        style={'text-align': 'right'},
        persistence=True,
        persistence_type='session',
        debounce=True,
        pattern=r'^(\d+)?[dD]?(\d+)$',
      ),
      dbc.Tooltip(
        'Set the number of shots (1, 2d6, d3, ...)',
        target=f'shots_addon_{self.tab_index}_{self.weapon_index}',
      ),
    ]

  def _damage_input(self):
    return [
      dbc.InputGroupAddon(
        'D',
        id=f'damage_addon_{self.tab_index}_{self.weapon_index}',
        addon_type='prepend'
      ),
      dbc.Input(
        type='text',
        id=f'damage_{self.tab_index}_{self.weapon_index}',
        value='2',
        style={'text-align': 'right'},
        persistence=True,
        persistence_type='session',
        debounce=True,
        pattern=r'^(\d+)?[dD]?(\d+)$',
      ),
      dbc.Tooltip(
        'Set the damage dealt (1, 2d6, d3, ...)',
        target=f'damage_addon_{self.tab_index}_{self.weapon_index}',
      ),
    ]

  def _modifier_rows(self):
    shot_modifier = dcc.Dropdown(
      options=self._shot_modifier_options(),
      multi=True,
      placeholder='Modify shot volume rolls',
      optionHeight=20,
      id=f'shotmods_{self.tab_index}_{self.weapon_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    hit_modifier = dcc.Dropdown(
      options=self._hit_modifier_options(),
      multi=True,
      placeholder='Modify hit rolls',
      optionHeight=20,
      id=f'hitmods_{self.tab_index}_{self.weapon_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    wound_modifier = dcc.Dropdown(
      options=self._wound_modifier_options(),
      multi=True,
      placeholder='Modify wound rolls',
      optionHeight=20,
      id=f'woundmods_{self.tab_index}_{self.weapon_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    save_modifier = dcc.Dropdown(
      options=self._save_modifier_options(),
      multi=True,
      placeholder='Modify save rolls',
      optionHeight=20,
      id=f'savemods_{self.tab_index}_{self.weapon_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    fnp_modifier = dcc.Dropdown(
      options=self._fnp_modifier_options(),
      multi=True,
      placeholder='Modify FNP rolls',
      optionHeight=20,
      id=f'fnpmods_{self.tab_index}_{self.weapon_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    damage_modifier = dcc.Dropdown(
      options=self._damage_modifier_options(),
      multi=True,
      placeholder='Modify damage rolls',
      optionHeight=20,
      id=f'damagemods_{self.tab_index}_{self.weapon_index}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    return [
      dbc.Row([dbc.Col(shot_modifier), dbc.Col(hit_modifier), dbc.Col(wound_modifier)], className="mb-2 "),
      dbc.Row([dbc.Col(save_modifier), dbc.Col(fnp_modifier), dbc.Col(damage_modifier)]),
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
      options.append({'label': f'Add +{i}', 'value': f'addvol_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i}', 'value': f'subvol_{i}'})
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
    for x in ['MW', 'hits', 'shots']:
      for i in range(1, 7):
        for j in range(2, 7):
          options.append({'label': f'+{i} {x} on a {j}+', 'value': f'addon_{i}_{x}_{j}_mod'})
    for x in ['MW', 'hits', 'shots']:
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
      {'label': f'Roll 2D6 and exceed toughness', 'value': f'smashagun'},
    ]
    for i in range(1, 7):
      options.append({'label': f'Add +{i}', 'value': f'add_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i}', 'value': f'sub_{i}'})
    # for i in range(2, 7):
    #   options.append({'label': f'Only wound on {i}+', 'value': f'lower_{i}'})
    for x in ['MW', 'wounds']:
      for i in range(1, 7):
        for j in range(2, 7):
          options.append({'label': f'+{i} {x} on a {j}+', 'value': f'addon_{i}_{x}_{j}_mod'})
    for x in ['MW', 'wounds']:
      for i in range(1, 7):
        for j in range(2, 7):
          values = ', '.join([str(x) for x in range(j, 7)])
          options.append({'label': f'+{i} {x} on a {values}', 'value': f'addon_{i}_{x}_{j}'})
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

  def _fnp_modifier_options(self):
    options = [
      {'label': f'Reroll all dice', 'value': f'reroll_all'},
      {'label': f'Reroll failed dice', 'value': f'reroll_failed'},
      {'label': f'Reroll one dice', 'value': f'reroll_one_dice'},
      {'label': f'Reroll ones', 'value': f'reroll_ones'},
    ]
    for i in range(1, 7):
      options.append({'label': f'Add +{i} to FNP', 'value': f'fnpadd_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i} to FNP', 'value': f'fnpsub_{i}'})
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
      options.append({'label': f'Add +{i}', 'value': f'addvol_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i}', 'value': f'subvol_{i}'})
    for i in range(2, 7):
      options.append({'label': f'Minimum {i} damage', 'value': f'minval_{i}'})
    return options
