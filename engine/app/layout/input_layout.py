import dash_bootstrap_components as dbc
import dash_core_components as dcc

from ...constants import TAB_COLOURS

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
* Added sub-plot for saviour protocols. Can be found under the save modifiers.
* Added sub-plot fot damage infliced from gets hot. Can be found under hit modifiers.


##### Todo:
* Figure out how to display the average values for sub-plots
* Figure out feed-forward abilities like rend (I legit think this may be impossible with how I have built the app.
Currently it assumes all dice rolls are independent however adding the feed-forward abilities changes that. If anyone out there knows how
it can be done I would be more than happy to implement it.)
* ???

There are no **ads** funding this, so please don't be a dick. Otherwise,
I hope you find this useful!
'''


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
        label='Info',
        style={'width': '100%'},
      )
    )
    return dbc.Tabs(
      tabs,
      className='nav-justified',
      style={'padding-top': '4px', 'padding-bottom': '0px'},
    )


class InputTabLayout(object):
  def __init__(self, tab_id, tab_count=0, weapon_count=0):
    self.tab_id = tab_id
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def layout(self):
    return dbc.Tab(
      self.tab_content(),
      id='tab_{}'.format(self.tab_id),
      label='Profile {}'.format(self.tab_id + 1),
      style={'width': '100%'},
      label_style={"color": TAB_COLOURS[self.tab_id]}
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
        dbc.Col(self._tab_enable_input(), width=2),
        dbc.Col(self._tab_name_input()),
        dbc.Col(self._points_input(), width=2),
        dbc.Col(self._average_output(), width=2),
        dbc.Col(self._standard_dev_output(), width=2),
      ],
      className='mb-2',
    )

  def _points_input(self):
    content = [
      dbc.InputGroupAddon("Points", addon_type="prepend"),
      dbc.Input(
        type="number",
        id=f'points_{self.tab_id}',
        value=1,
        debounce=True,
        min=1,
        persistence=True,
        persistence_type='session',
      ),
    ]
    return dbc.InputGroup(content, size="sm")

  def _average_output(self):
    return dbc.InputGroup(
      [
        dbc.InputGroupAddon("Mean", addon_type="prepend"),
        dbc.Input(
          type="text",
          id=f'avgdisplay_{self.tab_id}',
          value=f'Average',
          disabled=True
        ),
      ],
      size="sm",
    )

  def _standard_dev_output(self):
    return dbc.InputGroup(
      [
        dbc.InputGroupAddon("σ", addon_type="prepend"),
        dbc.Input(
          type="text",
          id=f'stddisplay_{self.tab_id}',
          value=f'Average',
          disabled=True
        ),
      ],
      size="sm",
    )

  def _tab_enable_input(self):
    content = [
      dbc.Select(
        options=[
          {"label": "Enabled", "value": 'enabled'},
          {"label": "Disabled", "value": 'disabled'}
        ],
        value='enabled' if self.tab_id == 0 else 'disabled',
        disabled=self.tab_id == 0,
        id=f'enabled_{self.tab_id}',
        persistence=True,
        persistence_type='session',
      )
    ]
    return dbc.InputGroup(content, size="sm")

  def _tab_name_input(self):
    content = [
      dbc.InputGroupAddon("Profile Name", addon_type="prepend"),
      dbc.Input(
        type="text",
        id=f'tabname_{self.tab_id}',
        value=f'Profile {self.tab_id}',
        debounce=True,
        minLength=2,
        persistence=True,
        persistence_type='session',
        maxLength=60
      ),
    ]
    return dbc.InputGroup(content, size="sm")

  def _target_input_row(self):
    presets = dbc.DropdownMenu(
      [
        dbc.DropdownMenuItem("Guardsmen", id=f'guardsman_{self.tab_id}'),
        dbc.DropdownMenuItem("Ork Boyz", id=f'ork_boy_{self.tab_id}'),
        dbc.DropdownMenuItem("Shield Drone", id=f'shield_drone_{self.tab_id}'),
        dbc.DropdownMenuItem("Tactical Marine", id=f'tactical_marine_{self.tab_id}'),
        dbc.DropdownMenuItem("Intercessor", id=f'intercessor_{self.tab_id}'),
        dbc.DropdownMenuItem("Terminator", id=f'terminator_{self.tab_id}'),
        dbc.DropdownMenuItem("Crisis Suit", id=f'crisis_suit_{self.tab_id}'),
        dbc.DropdownMenuItem("Custode", id=f'custode_{self.tab_id}'),
        dbc.DropdownMenuItem("Riptide", id=f'riptide_{self.tab_id}'),
        dbc.DropdownMenuItem("Rhino", id=f'rhino_{self.tab_id}'),
        dbc.DropdownMenuItem("Leman Russ", id=f'leman_russ_{self.tab_id}'),
        dbc.DropdownMenuItem("Knight", id=f'knight_{self.tab_id}'),
      ],
      label="Presets",
      bs_size='sm',
      color="secondary",
      addon_type='prepend'
    )
    content = dbc.InputGroup(
      [
        presets,
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
      dbc.InputGroupAddon('T', id=f'toughness_addon_{self.tab_id}', addon_type='prepend'),
      dbc.Select(
        id=f'toughness_{self.tab_id}',
        options=[{'label': f'{i}', 'value': i} for i in range(1,11)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the toughness of the target',
        target=f'toughness_addon_{self.tab_id}',
      ),
    ]

  def _save_input(self):
    return [
      dbc.InputGroupAddon('SV', id=f'save_addon_{self.tab_id}', addon_type='prepend'),
      dbc.Select(
        id=f'save_{self.tab_id}',
        options=[{'label': f'{i}+', 'value': i} for i in range(2,8)],
        value=3,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the save value of the target',
        target=f'save_addon_{self.tab_id}',
      ),
    ]

  def _invuln_input(self):
    return [
      dbc.InputGroupAddon('INV', id=f'invuln_addon_{self.tab_id}', addon_type='prepend'),
      dbc.Select(
        id=f'invuln_{self.tab_id}',
        options=[{'label': f'{i}++', 'value': i} for i in range(2,8)],
        value=7,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the invulnerable save value of the target',
        target=f'invuln_addon_{self.tab_id}',
      ),
    ]

  def _fnp_input(self):
    return [
      dbc.InputGroupAddon('FNP', id=f'fnp_addon_{self.tab_id}', addon_type='prepend'),
      dbc.Select(
        id=f'fnp_{self.tab_id}',
        options=[{'label': f'{i}+++', 'value': i} for i in range(2,8)],
        value=7,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the feel no pain value of the target',
        target=f'fnp_addon_{self.tab_id}',
      ),
    ]

  def _wounds_input(self):
    return [
      dbc.InputGroupAddon('W', id=f'wounds_addon_{self.tab_id}', addon_type='prepend'),
      dbc.Select(
        id=f'wounds_{self.tab_id}',
        options=[{'label': f'{i}', 'value': i} for i in range(1,25)],
        value=2,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the target wounds value',
        target=f'wounds_addon_{self.tab_id}',
      ),
    ]

  def _weapon_tabs(self):
    weapon_tabs = []
    for weapon_id in range(self.weapon_count):
      weapon_tab = WeaponTabLayout(
        self.tab_id,
        weapon_id,
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
  def __init__(self, tab_id, weapon_id, tab_count=0, weapon_count=0):
    self.tab_id = tab_id
    self.weapon_id = weapon_id
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def layout(self):
    return dbc.Tab(
      self._tab_content(),
      id=f'weapontab_{self.tab_id}_{self.weapon_id}',
      label='Weapon {}'.format(self.weapon_id + 1),
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
        dbc.Col(self._average_output(), width=2),
        dbc.Col(self._standard_dev_output(), width=2),
      ],
      className='mb-2',
    )

  def _average_output(self):
    return dbc.InputGroup(
      [
        dbc.InputGroupAddon("Mean", addon_type="prepend"),
        dbc.Input(
          type="text",
          id=f'wepavgdisplay_{self.tab_id}_{self.weapon_id}',
          value=f'Average',
          disabled=True
        ),
      ],
      size="sm",
    )

  def _standard_dev_output(self):
    return dbc.InputGroup(
      [
        dbc.InputGroupAddon("σ", addon_type="prepend"),
        dbc.Input(
          type="text",
          id=f'wepstddisplay_{self.tab_id}_{self.weapon_id}',
          value=f'Average',
          disabled=True
        ),
      ],
      size="sm",
    )

  def _weapon_enable_input(self):
    return dbc.InputGroup([
      dbc.Select(
        options=[
          {'label': 'Enabled', 'value': 'enabled'},
          {'label': 'Disabled', 'value': 'disabled'}
        ],
        value='enabled' if self.weapon_id == 0 else 'disabled',
        disabled=self.weapon_id == 0,
        persistence=True,
        persistence_type='session',
        id=f'weaponenabled_{self.tab_id}_{self.weapon_id}',
      ),
    ], size="sm")

  def _weapon_name_input(self):
    return dbc.InputGroup([
      dbc.InputGroupAddon("Weapon Name", addon_type="prepend"),
      dbc.Input(
        type="text",
        id=f'weaponname_{self.tab_id}_{self.weapon_id}',
        value=f'Weapon {self.weapon_id+1}',
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
        'BS',
        id=f'ws_addon_{self.tab_id}_{self.weapon_id}',
        addon_type='prepend'
      ),
      dbc.Select(
        id=f'ws_{self.tab_id}_{self.weapon_id}',
        options=[{'label': f'{i}+', 'value': i} for i in range(1,8)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the weapons skill value',
        target=f'ws_addon_{self.tab_id}_{self.weapon_id}',
      ),
    ]

  def _strength_input(self):
    return [
      dbc.InputGroupAddon(
        'S',
        id=f'strength_addon_{self.tab_id}_{self.weapon_id}',
        addon_type='prepend'
      ),
      dbc.Select(
        id=f'strength_{self.tab_id}_{self.weapon_id}',
        options=[{'label': f'{i}', 'value': i} for i in range(1,21)],
        value=4,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the strength value',
        target=f'strength_addon_{self.tab_id}_{self.weapon_id}',
      ),
    ]

  def _ap_input(self):
    return [
      dbc.InputGroupAddon(
        'AP',
        id=f'ap_addon_{self.tab_id}_{self.weapon_id}',
        addon_type="prepend"
      ),
      dbc.Select(
        id=f'ap_{self.tab_id}_{self.weapon_id}',
        options=[{'label': '0' if i==0 else f'-{i}', 'value': i} for i in range(0,7)],
        value=1,
        persistence=True,
        persistence_type='session',
      ),
      dbc.Tooltip(
        'Set the AP value',
        target=f'ap_addon_{self.tab_id}_{self.weapon_id}',
      ),
    ]

  def _shots_input(self):
    return [
      dbc.InputGroupAddon(
        '#',
        id=f'shots_addon_{self.tab_id}_{self.weapon_id}',
        addon_type="prepend"
      ),
      dbc.Input(
        type='text',
        id=f'shots_{self.tab_id}_{self.weapon_id}',
        value='2d6',
        style={'text-align': 'right'},
        persistence=True,
        persistence_type='session',
        debounce=True,
        pattern=r'^(\d+)?[dD]?(\d+)$',
      ),
      dbc.Tooltip(
        'Set the number of shots (1, 2d6, d3, ...)',
        target=f'shots_addon_{self.tab_id}_{self.weapon_id}',
      ),
    ]

  def _damage_input(self):
    return [
      dbc.InputGroupAddon(
        'D',
        id=f'damage_addon_{self.tab_id}_{self.weapon_id}',
        addon_type='prepend'
      ),
      dbc.Input(
        type='text',
        id=f'damage_{self.tab_id}_{self.weapon_id}',
        value='2',
        style={'text-align': 'right'},
        persistence=True,
        persistence_type='session',
        debounce=True,
        pattern=r'^(\d+)?[dD]?(\d+)$',
      ),
      dbc.Tooltip(
        'Set the damage dealt (1, 2d6, d3, ...)',
        target=f'damage_addon_{self.tab_id}_{self.weapon_id}',
      ),
    ]

  def _modifier_rows(self):
    shot_modifier = dcc.Dropdown(
      options=self._shot_modifier_options(),
      multi=True,
      placeholder='Modify shot volume rolls',
      optionHeight=20,
      id=f'shotmods_{self.tab_id}_{self.weapon_id}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    hit_modifier = dcc.Dropdown(
      options=self._hit_modifier_options(),
      multi=True,
      placeholder='Modify hit rolls',
      optionHeight=20,
      id=f'hitmods_{self.tab_id}_{self.weapon_id}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    wound_modifier = dcc.Dropdown(
      options=self._wound_modifier_options(),
      multi=True,
      placeholder='Modify wound rolls',
      optionHeight=20,
      id=f'woundmods_{self.tab_id}_{self.weapon_id}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    save_modifier = dcc.Dropdown(
      options=self._save_modifier_options(),
      multi=True,
      placeholder='Modify save rolls',
      optionHeight=20,
      id=f'savemods_{self.tab_id}_{self.weapon_id}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    fnp_modifier = dcc.Dropdown(
      options=self._fnp_modifier_options(),
      multi=True,
      placeholder='Modify FNP rolls',
      optionHeight=20,
      id=f'fnpmods_{self.tab_id}_{self.weapon_id}',
      persistence=True,
      persistence_type='session',
      value=[],
    )
    damage_modifier = dcc.Dropdown(
      options=self._damage_modifier_options(),
      multi=True,
      placeholder='Modify damage rolls',
      optionHeight=20,
      id=f'damagemods_{self.tab_id}_{self.weapon_id}',
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
      {'label': f'Suffer MW on a hit roll of 1', 'value': f'overheat'},
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
      {'label': f'Saviour Protocol', 'value': f'normaldrone'},
      {'label': f'Saviour Protocol (Shield)', 'value': f'shielddrone'},
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
      {'label': f'Add +D6', 'value': f'addvol_d6'},
      {'label': f'Add +D3', 'value': f'addvol_d3'},
    ]
    for i in range(1, 7):
      options.append({'label': f'Add +{i}', 'value': f'addvol_{i}'})
    for i in range(1, 7):
      options.append({'label': f'Sub -{i}', 'value': f'subvol_{i}'})
    for i in range(2, 7):
      options.append({'label': f'Minimum {i} damage', 'value': f'minval_{i}'})
    return options


