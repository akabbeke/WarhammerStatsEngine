import dash
import dash_daq as daq
import re
import dash_core_components as dcc
import dash_html_components as html
from urllib.parse import urlparse, parse_qsl, urlencode
from dash.dependencies import Input, Output, State

from .layout import GraphLayout, InputGenerator, Layout

from .util import compute

from ..constants import TAB_COUNT

class URLMinify(object):
  def __init__(self, tab_count):
    self.tab_count = tab_count
    self.mapping = [
      *self.data_row(),
      *self.target_row(),
      *self.attack_row(),
      *self.modify_row(),
    ]

  def minify(self, key):
    return self.to_min().get(key, key)

  def maxify(self, key):
    return self.to_max().get(key, key)

  def to_min(self):
    return {x:y for x, y in self.mapping}

  def to_max(self):
    return {y:x for x, y in self.mapping}

  def data_row(self):
    row = []
    for i in range(self.tab_count):
      row += self.data_row_input(i)
    return row

  def data_row_input(self, tab_index):
    return [
      [f'enabled_{tab_index}', f'e_{tab_index}'],
      [f'tab_name_{tab_index}', f'tn_{tab_index}'],
    ]

  def target_row(self):
    row = []
    for i in range(self.tab_count):
      row += self.target_row_input(i)
    return row

  def target_row_input(self, tab_index):
    return [
      [f'toughness_{tab_index}', f't_{tab_index}'],
      [f'save_{tab_index}', f'sv_{tab_index}'],
      [f'invuln_{tab_index}', f'inv_{tab_index}'],
      [f'fnp_{tab_index}', f'fn_{tab_index}'],
      [f'wounds_{tab_index}', f'w_{tab_index}'],
    ]

  def attack_row(self):
    row = []
    for i in range(self.tab_count):
      row += self.attack_row_input(i)
    return row

  def attack_row_input(self, tab_index):
    return [
      [f'ws_{tab_index}', f'ws_{tab_index}'],
      [f'strength_{tab_index}', f's_{tab_index}'],
      [f'ap_{tab_index}', f'ap_{tab_index}'],
      [f'shots_{tab_index}', f'sh_{tab_index}'],
      [f'damage_{tab_index}', f'dm_{tab_index}'],
    ]

  def modify_row(self):
    row = []
    for i in range(self.tab_count):
      row += self.modify_input(i)
    return row

  def modify_input(self, tab_index):
    return [
      [f'shot_mods_{tab_index}', f'shm_{tab_index}'],
      [f'hit_mods_{tab_index}', f'hm_{tab_index}'],
      [f'wound_mods_{tab_index}', f'wm_{tab_index}'],
      [f'save_mods_{tab_index}', f'svm_{tab_index}'],
      [f'damage_mods_{tab_index}', f'dmm_{tab_index}'],
    ]



class CallbackMapper(object):
  def __init__(self, outputs=None, inputs=None, states=None):
    self._outputs = outputs or {}
    self._outputs_order = sorted(self._outputs.keys())
    self._inputs = inputs or {}
    self._inputs_order = sorted(self._inputs.keys())
    self._states = states or {}
    self._states_order = sorted(self._states.keys())

  @property
  def outputs(self):
    return [Output(k, self._outputs[k]) for k in self._outputs_order]

  @property
  def inputs(self):
    return [Input(k, self._inputs[k]) for k in self._inputs_order]

  @property
  def states(self):
    return [State(k, self._states[k]) for k in self._states_order]

  def input_to_kwargs_by_tab(self, args, tab_count):
    inputs = self.input_to_kwargs(args)
    tab_inputs = {i: {'inputs': {}, 'states': {}} for i in range(-1, tab_count)}
    for k in inputs['inputs']:
      match = re.match(r'(.*)_(\d+).*', k)
      if match:
        name, number = match.groups()
        tab_inputs[int(number)]['inputs'][name] = inputs['inputs'][k]
      else:
        tab_inputs[-1]['inputs'][k] = inputs['inputs'][k]
    for k in inputs['states']:
      match = re.match(r'(.*)_(\d+).*', k)
      if match:
        name, number = match.groups()
        tab_inputs[int(number)]['states'][name] = inputs['states'][k]
      else:
        tab_inputs[-1]['states'][k] = inputs['states'][k]
    return tab_inputs

  def input_to_kwargs(self, args):
    input_dict = {}
    state_dict = {}
    for i, key in enumerate(self._inputs_order):
      input_dict[key] = args[i]
    for j, key in enumerate(self._states_order):
      state_dict[key] = args[len(self._inputs_order) + j]
    return {'inputs': input_dict, 'states': state_dict}

  def dict_to_output(self, outputs):
    return [outputs[k] for k in self._outputs_order]


class CallbackController(object):
  def __init__(self, app, tab_count):
    self.app = app
    self.tab_count = tab_count
    self.layout_generator = Layout(self.tab_count)
    self.graph_layout = GraphLayout()
    self.input_generator = InputGenerator()
    self.url_minify = URLMinify(self.tab_count)

  def setup_callbacks(self):
    self.setup_url_callbacks()
    self.setup_graph_callbacks()
    self.setup_input_callbacks()
    self.setup_static_link_callbacks()
    self.setup_static_graph_callbacks()

  def setup_url_callbacks(self):
    mapper = CallbackMapper(outputs={'page-content': 'children'}, inputs={'url': 'pathname'})
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def page_content(pathname):
      result_dict = {}
      if pathname == '/':
        result_dict['page-content'] = self.layout_generator.base_layout()
      elif pathname == '/static':
        result_dict['page-content'] = self.layout_generator.static_layout()
      return mapper.dict_to_output(result_dict)

  def setup_graph_callbacks(self):
    inputs = self.input_generator.graph_inputs(self.tab_count)
    inputs.update({'url': 'href'})
    mapper = CallbackMapper(
      outputs=self._graph_updates(),
      inputs=self.input_generator.graph_inputs(self.tab_count),
      states=self._graph_updates(),
    )
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def graph_callback(*args):
      tab_data = mapper.input_to_kwargs_by_tab(args, self.tab_count)
      result_dict = self.update_graph(tab_data)
      return mapper.dict_to_output(result_dict)

  def setup_static_graph_callbacks(self):
    mapper = CallbackMapper(
      outputs={'page-2-content': 'children', 'static_damage_graph': 'figure'},
      inputs={'url': 'href', 'page-2-radios': 'value'},
    )
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def static_graph_callback(*args):
      tab_data = mapper.input_to_kwargs(args)
      url_args = self.parse_url_params(tab_data['inputs']['url'])
      graph_args = self.parse_static_graph_args(url_args)
      output = {
        'page-2-content': str(graph_args),
        'static_damage_graph': self.update_static_graph(graph_args),
        }
      return mapper.dict_to_output(output)

  def parse_url_params(self, url):
    parse_result = urlparse(url)
    params = parse_qsl(parse_result.query)
    state = dict(params)
    max_map = self.url_minify.to_max()
    return {max_map.get(x, x):y for x,y in state.items()}

  def parse_static_graph_args(self, graph_args):
    foo = {}
    for key, value in graph_args.items():
      match = re.match(r'(?P<sub_key>.+)_(?P<tab_index>\d+)', key)
      if match:
        sub_key = match.groupdict().get('sub_key')
        tab_index = int(match.groupdict().get('tab_index'))
        if sub_key in ['shot_mods', 'hit_mods','wound_mods', 'save_mods', 'damage_mods']:
          value = value.split(',')
        if tab_index in foo:
          foo[tab_index][sub_key] = value
        else:
          foo[tab_index] = {sub_key: value}
      else:
        if -1 in foo:
          foo[-1][key] = value
        else:
          foo[-1] = {key: value}

    return foo

  def setup_static_link_callbacks(self):
    mapper = CallbackMapper(
      outputs={'permalink': 'href'},
      inputs=self.input_generator.graph_inputs(self.tab_count),
    )
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def static_graph_callback(*args):
      tab_data = mapper.input_to_kwargs_by_tab(args, self.tab_count)
      result_dict = {'permalink': self.convert_args_to_url(tab_data)}
      return mapper.dict_to_output(result_dict)

  def convert_args_to_url(self, tab_data):
    url_args = {}
    for tab_index in tab_data:
      tab_data[tab_index]['inputs']
      if tab_data[tab_index]['inputs'].get('enabled'):
        for key, value in tab_data[tab_index]['inputs'].items():
          if key in ['shot_mods', 'hit_mods','wound_mods', 'save_mods', 'damage_mods']:
            url_args[f'{key}_{tab_index}'] = ','.join(value or [])
          else:
            url_args[f'{key}_{tab_index}'] = value
    url_args.update(tab_data[-1]['inputs'])
    min_map = self.url_minify.to_min()
    url_args = {min_map.get(x, x):y for x,y in url_args.items()}
    state = urlencode(url_args)
    return f'/static?{state}'

  def _graph_updates(self):
    return {
      **{'damage_graph': 'figure'},
      **{f'avg_display_{i}': 'children' for i in range(self.tab_count)},
      **{f'std_display_{i}': 'children' for i in range(self.tab_count)},
    }


  def setup_input_callbacks(self):
    for i in range(self.tab_count):
      self.setup_input_tab_callback(i)

  def setup_input_tab_callback(self, tab_index):
    self.disable_callback(tab_index)
    self.tab_name_callback(tab_index)

  def disable_callback(self, tab_index):
    @self.app.callback(
      self._disable_outputs(tab_index),
      [Input('enabled_{}'.format(tab_index), 'checked')],
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

  def update_static_graph(self, graph_args):
    title = graph_args.get(-1, {}).get('title')
    if not graph_args:
      return self.graph_layout.figure_template()
    graph_data = []
    for tab_index in [x for x in sorted(graph_args.keys()) if x != -1]:
      data = compute(
        **graph_args[tab_index],
        existing_data=graph_args,
        re_render=True,
        tab_index=tab_index,
      )
      graph_data.append(data.get('graph_data'))

    max_len = max(max([len(x.get('x', [])) for x in graph_data]), 20)
    return self.graph_layout.figure_template(graph_data, max_len, title)

  def update_graph(self, tab_data):
    graph_data = tab_data[-1]['states']['damage_graph']['data']
    output = {}
    if graph_data == [{}] * self.tab_count:
      changed_tabs = list(range(self.tab_count))
    else:
      changed_tabs = self.tabs_changed()
    for tab_index in range(self.tab_count):
      data = compute(
        **tab_data[tab_index]['inputs'],
        existing_data=graph_data,
        re_render=tab_index in changed_tabs,
        tab_index=tab_index,
      )
      graph_data[tab_index] = data.get('graph_data')
      if data.get('mean') is not None:
        output[f'avg_display_{tab_index}'] = 'Mean: {}'.format(round(data['mean'], 2))
      else:
        output[f'avg_display_{tab_index}'] = tab_data[tab_index]['states']['avg_display']

      if data.get('std') is not None:
        output[f'std_display_{tab_index}'] = 'σ: {}'.format(round(data['std'], 2))
      else:
        output[f'std_display_{tab_index}'] = tab_data[tab_index]['states']['std_display']

    max_len = max(max([len(x.get('x', [])) for x in graph_data]), 20)
    output['damage_graph'] = self.graph_layout.figure_template(graph_data, max_len)
    return output

  def tabs_changed(self):
    ctx = dash.callback_context
    if not ctx:
      return list(range(TAB_COUNT))
    tabs = []
    for trigger in ctx.triggered:
      match = re.match(r'.*_(\d+).*', trigger['prop_id'])
      if match and 'tab_name' not in trigger['prop_id']:
        tabs.append(int(match.groups()[0]))
    return list(set(tabs))