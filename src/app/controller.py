import dash
import dash_daq as daq
import re
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from .layout import GraphLayout, InputGenerator, MultiOptionGenerator

from .util import compute

from ..constants import TAB_COUNT

def parse_args(args):
  mapped_args = []
  for i in range(0, TAB_COUNT):
    tab_dict = {}
    tab_inputs = InputGenerator().gen_tab_inputs(i)
    trim_length = -1 * len('-{}'.format(i))
    for j, input_name in enumerate(tab_inputs):
      tab_dict[input_name[:trim_length]] = args[(len(tab_inputs)*i) + j]
    mapped_args.append(tab_dict)
  return mapped_args

def update_graph(*args):
  graph_args = parse_args(args[:-1])
  graph_data = args[-1]['data']

  if graph_data == [{}] * TAB_COUNT:
    tab_numbers = list(range(TAB_COUNT))
  else:
    tab_numbers = determine_which_tabs_changed(dash.callback_context)
  for tab_number in tab_numbers:
    values = compute(**graph_args[tab_number])
    graph_data[tab_number] = {
      'x': [i for i, x in enumerate(values)],
      'y': [100*x for i, x in enumerate(values)],
      'name': 'P{}'.format(tab_number),
    }

  max_len = max(max([len(x.get('x', [])) for x in graph_data]), 24)

  return GraphLayout().figure_template(graph_data, max_len)

def determine_which_tabs_changed(ctx):
  if not ctx:
    return list(range(TAB_COUNT))
  tabs = []
  for trigger in ctx.triggered:
    match = re.match(r'.*_(\d+).*', trigger['prop_id'])
    if match:
      tabs.append(int(match.groups()[0]))
  return list(set(tabs))

class CallbackController(object):
  def __init__(self, app, tab_count):
    self.app = app
    self.tab_count = tab_count
    self.input_generator = InputGenerator()
    self.multi_generator = MultiOptionGenerator()

  def graph_inputs(self):
    return self.input_generator.graph_inputs(self.tab_count)

  def setup_callbacks(self):
    self.setup_graph_callbacks()
    self.setup_input_callbacks()

  def setup_graph_callbacks(self):
    @self.app.callback(
      Output('damage-graph', 'figure'),
      [Input(x, 'value') for x in self.graph_inputs()],
      [State('damage-graph', 'figure')]
    )
    def graph_callback(*args):
      return update_graph(*args)

  def setup_input_callbacks(self):
    for i in range(self.tab_count):
      self.setup_input_tab_callback(i)

    # self.lock_target_callback()

  def setup_input_tab_callback(self, tab_index):
    self.disable_callback(tab_index)
    self.tab_name_callback(tab_index)
    self.shot_mods_callback(tab_index)
    self.hit_mods_callback(tab_index)
    self.wound_mods_callback(tab_index)
    self.save_mods_callback(tab_index)
    self.damage_mods_callback(tab_index)

  def disable_callback(self, tab_index):
    @self.app.callback(
      self._disable_outputs(tab_index),
      [Input('enable_{}'.format(tab_index), 'value')],
    )
    def disable_tab_options(enable):
        return [not enable] * 15

  def _disable_outputs(self, tab_index):
    ids = ['damage_mods_{}', 'save_mods_{}', 'wound_mods_{}', 'hit_mods_{}', 'shot_mods_{}',
           'ws_{}', 'toughness_{}', 'strength_{}', 'ap_{}', 'save_{}', 'invuln_{}', 'fnp_{}',
           'wounds_{}', 'shots_{}', 'damage_{}']
    return [Output(x.format(tab_index), 'disabled') for x in ids]


  def tab_name_callback(self, tab_index):
    @self.app.callback(
      Output('tab_{}'.format(tab_index), 'label'),
      [Input('tab_name_{}'.format(tab_index), 'value')],
    )
    def update_tab_name(value):
        return value if len(value) > 2 else 'Profile'


  def shot_mods_callback(self, tab_index):
    @self.app.callback(
      Output('shot_mods_{}'.format(tab_index), 'options'),
      [Input('shot_mods_{}'.format(tab_index), 'value')],
    )
    def update_shot_options(value):
      return self.multi_generator.shot_options(value or [])

  def hit_mods_callback(self, tab_index):
    @self.app.callback(
      Output('hit_mods_{}'.format(tab_index), 'options'),
      [Input('hit_mods_{}'.format(tab_index), 'value')],
    )
    def update_hit_options(value):
      return self.multi_generator.hit_options(value or [])

  def wound_mods_callback(self, tab_index):
    @self.app.callback(
      Output('wound_mods_{}'.format(tab_index), 'options'),
      [Input('wound_mods_{}'.format(tab_index), 'value')],
    )
    def update_wound_options(value):
      return self.multi_generator.wound_options(value or [])

  def save_mods_callback(self, tab_index):
    @self.app.callback(
      Output('save_mods_{}'.format(tab_index), 'options'),
      [Input('save_mods_{}'.format(tab_index), 'value')],
    )
    def update_save_options(value):
      return self.multi_generator.save_options(value or [])

  def damage_mods_callback(self, tab_index):
    @self.app.callback(
      Output('damage_mods_{}'.format(tab_index), 'options'),
      [Input('damage_mods_{}'.format(tab_index), 'value')],
    )
    def update_damage_options(value):
      return MultiOptionGenerator().damage_options(value or [])

  def lock_target_callback(self):
    @self.app.callback(
      self.generate_lock_target_outputs(),
      self.generate_lock_target_inputs(),
      self.generate_lock_target_states(),
    )
    def update_damage_options(*args):
      input_len = len(self.input_generator.target_row_input(0))
      tab_numbers = determine_which_tabs_changed(dash.callback_context)
      print(tab_numbers)
      if len(tab_numbers) > 1:
        return args[self.tab_count:]
      else:
        fixed = args[self.tab_count:][tab_numbers[0] * input_len: (tab_numbers[0] + 1) * input_len]
        return fixed * self.tab_count


  def generate_lock_target_outputs(self):
    outputs = []
    for i in range(TAB_COUNT):
      outputs += [Output(y, 'value') for y in self.input_generator.target_row_input(i)]
    return outputs

  def generate_lock_target_inputs(self):
    return [Input('target_apply_all_{}'.format(i), 'n_clicks') for i in range(self.tab_count)]

  def generate_lock_target_states(self):
    states = []
    for i in range(TAB_COUNT):
      states += [State(y, 'value') for y in self.input_generator.target_row_input(i)]
    return states