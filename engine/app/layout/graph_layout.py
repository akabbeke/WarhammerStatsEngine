
import dash_core_components as dcc
import dash_bootstrap_components as dbc

from ...constants import TAB_COUNT, GA_TRACKING_ID, TAB_COLOURS, DEFAULT_GRAPH_PLOTS


app_color = {"graph_bg": "#082255", "graph_line": "#a3a7b0"}


class GraphLayout(object):
  def __init__(self, tab_count=0):
    self.tab_count = tab_count
    self.graph_count = 2

  def layout(self):
    content = dcc.Graph(
      id='damage_graph',
      style={'height':'50vh'},
      figure=self.figure_template(top=10),
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

  def _tab_info(self, tab_id, callback, average, std):
    tab_inputs = callback.tab_inputs[tab_id]
    ''''damagemods': ['addvol_d6'], 'fnpmods': ['fnpadd_2'], 'hitmods': ['reroll_ones'], 'savemods': ['normaldrone'], 'shotmods': ['reroll_ones'], 'shots': '2d6', 'strength': '4', 'weaponenabled': 'enabled', 'woundmods': ['add_2']'''
    weapon_rows = []
    print(tab_inputs)
    for k, weapon in tab_inputs['weapons'].items():
      weapon_rows.append(
        self._weapon_output(
          weapon['strength'],
          weapon['ap'],
          weapon['ws'],
          weapon['shots'],
          weapon['damage'],
          weapon.get('shotmods'),
          weapon.get('hitmods'),
          weapon.get('woundmods'),
          weapon.get('savemods'),
          weapon.get('fnpmods'),
          weapon.get('damagemods'),
        )
      )
    return dbc.Col([self._target_output(
        tab_inputs['tabname'],
        tab_inputs['points'],
        tab_inputs['toughness'],
        tab_inputs['save'],
        tab_inputs['invuln'],
        tab_inputs['fnp'],
        tab_inputs['wounds'],
        round(average, 2),
        round(std, 2),
      ),
      dbc.Col(weapon_rows),
    ], className='mb-2',)


  def _tab_output(self, name, points, average, std):
    return [
      dbc.Col(self._make_group(self._output_pill('Name', name))),
      dbc.Col(self._make_group(self._output_pill('Pts', points)), width=2),
      dbc.Col(self._make_group(self._output_pill('Avg', average)), width=2),
      dbc.Col(self._make_group(self._output_pill('Std', std)), width=2),
    ]

  def _weapon_output(self, strength, ap, bs, number, damage, shotmod, hitmod, woundmod, savemod, fnpmod, damagemod):
    mods = []
    if shotmod:
      mods.append(dbc.Row(self._make_group(self._output_pill('Shot Modifiers', ', '.join(shotmod)))))
    if hitmod:
      mods.append(dbc.Row(self._make_group(self._output_pill('Hit Modifiers', ', '.join(hitmod)))))
    if woundmod:
      mods.append(dbc.Row(self._make_group(self._output_pill('Wound Modifiers', ', '.join(woundmod)))))
    if savemod:
      mods.append(dbc.Row(self._make_group(self._output_pill('Save Modifiers', ', '.join(savemod)))))
    if fnpmod:
      mods.append(dbc.Row(self._make_group(self._output_pill('FNP Modifiers', ', '.join(fnpmod)))))
    if damagemod:
      mods.append(dbc.Row(self._make_group(self._output_pill('Damage Modifiers', ', '.join(damagemod)))))

    weapon_group = self._make_group(
      [
        *self._output_pill('S', strength),
        *self._output_pill('AP', f'-{ap}'),
        *self._output_pill('BS', f'{bs}+'),
        *self._output_pill('#', number),
        *self._output_pill('D', damage),
      ],
    )
    return dbc.Row(dbc.Col([weapon_group, dbc.Col(mods, className='mb-2')]))


  def _target_output(self, name, points, toughness, save, invuln, fnp, wounds, avg, std):
    return dbc.Row([
      dbc.Col(self._make_group(
        dbc.Input(type="text", value=name, disabled=True),
      ), width=3),
      dbc.Col(self._make_group(
        [
          *self._output_pill('PTS', points),
          *self._output_pill('T', toughness),
          *self._output_pill('SV', f'{save}+'),
          *self._output_pill('INV', f'{invuln}++'),
          *self._output_pill('FNP', f'{fnp}+++'),
          *self._output_pill('W', wounds),
          *self._output_pill('Mean', avg),
          *self._output_pill('σ', std),
        ]
      ), className='mb-2'),
    ], className='mb-2',)

  def _make_group(self, content):
    return dbc.InputGroup(content, size="sm")

  def _output_pill(self, name, value):
    return [
      dbc.InputGroupAddon(name, addon_type="prepend"),
      dbc.Input(type="text", value=value, disabled=True),
    ]

  def static_layout(self):
    content = dcc.Graph(
      id='static_damage_graph',
      style={'height':'80vh'},
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

  def embed_layout(self):
    content = dcc.Graph(
      id='static_damage_graph',
      style={'height':'95vh'},
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
      },
    )
    return content

  def figure_template(self, data=None, max_len=10, dtick=None, title=None, static=False, top=50):
    return {
      'data': data or DEFAULT_GRAPH_PLOTS,
      'layout': {
        'title': title,
        'showlegend': True,
        'legend': dict(orientation='h',yanchor='top',xanchor='center',y=1, x=0.5),
        # 'template': 'plotly_dark',
        'xaxis': {
            'title': 'Minimum Wounds Dealt',
            'type': 'linear',
            'range': [0, max_len],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': dtick,
            # "gridcolor": app_color["graph_line"],
            # "color": app_color["graph_line"],
            'fixedrange': True,
        },
        'yaxis': {
            'title': 'Probability of Minimum Wounds Dealt',
            'type': 'linear',
            'range': [0, 100],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 10,
            # "gridcolor": app_color["graph_line"],
            # "color": app_color["graph_line"],
            'fixedrange': True,
        },
        'margin':{
          'l': 70,
          'r': 70,
          'b': 50,
          't': top,
          'pad': 4,
        },
        'autosize': True,
      },
    }

