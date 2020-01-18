from collections import defaultdict

import dash
import dash_daq as daq
import re
import dash_core_components as dcc
import dash_html_components as html
from urllib.parse import urlparse, parse_qsl, urlencode
from dash.dependencies import Input, Output, State

from .layout import GraphLayout, Layout

from .util import ComputeController, URLMinify, InputGenerator

from ..constants import TAB_COUNT
from ..stats.pmf import PMF

def recurse_default():
  return defaultdict(recurse_default)

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

  def input_to_kwargs_by_tab(self, args, tab_count, weapon_count):
    inputs = self.input_to_kwargs(args)
    parsed_inputs = recurse_default()
    parsed_inputs = self.parse_kwargs(inputs, parsed_inputs, 'inputs')
    parsed_inputs = self.parse_kwargs(inputs, parsed_inputs, 'states')
    return self.default_to_regular(parsed_inputs)

  def default_to_regular(self, d):
    if isinstance(d, defaultdict):
        d = {k: self.default_to_regular(v) for k, v in d.items()}
    return d

  def parse_kwargs(self, inputs, parsed_inputs=None, parse_field=None):
    parsed_inputs = parsed_inputs or recurse_default()
    parse_field = parse_field or 'inputs'
    for raw_input_name, value in inputs[parse_field].items():
      match = re.match(r'(?P<input_name>[^_]+)_(?P<tab>\d+)(_(?P<weapon>\d+))?', raw_input_name)
      if match:
        input_name = match.groupdict().get('input_name')
        tab = match.groupdict().get('tab')
        weapon = match.groupdict().get('weapon')
        if weapon:
          parsed_inputs[int(tab)]['weapons'][int(weapon)][parse_field][input_name] = value
        else:
          parsed_inputs[int(tab)][parse_field][input_name] = value
      else:
        parsed_inputs[-1][parse_field][raw_input_name] = value
    return parsed_inputs

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


class URLCallbackController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.layout_generator = Layout(self.tab_count)

  def setup_callbacks(self):
    mapper = CallbackMapper(outputs={'page_content': 'children'}, inputs={'url': 'pathname'})
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def page_content(pathname):
      result_dict = {}
      if pathname == '/':
        result_dict['page_content'] = self.layout_generator.base_layout()
      elif pathname == '/static':
        result_dict['page_content'] = self.layout_generator.static_layout()
      return mapper.dict_to_output(result_dict)


class GraphCallbackController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.input_generator = InputGenerator()
    self.graph_layout_generator = GraphLayout()
    self.compute_controller = ComputeController()

  def setup_callbacks(self):
    inputs = self.input_generator.graph_inputs(self.tab_count, self.weapon_count)
    inputs.update({'url': 'href'})
    mapper = CallbackMapper(
      outputs=self._graph_updates(),
      inputs=self.input_generator.graph_inputs(self.tab_count, self.weapon_count),
      states=self._graph_updates(),
    )
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def graph_callback(*args):
      tab_data = mapper.input_to_kwargs_by_tab(args, self.tab_count, self.weapon_count)
      result_dict = self._update_graph(tab_data)
      return mapper.dict_to_output(result_dict)

  def _graph_updates(self):
    return {
      **{'damage_graph': 'figure'},
      **{f'avgdisplay_{i}': 'children' for i in range(self.tab_count)},
      **{f'stddisplay_{i}': 'children' for i in range(self.tab_count)},
    }

  def _update_graph(self, tab_data):
    graph_data = tab_data[-1]['states']['damage_graph']['data']
    output = {}
    if graph_data == [{}] * self.tab_count:
      changed_tabs = list(range(self.tab_count))
    else:
      changed_tabs = self._tabs_changed()
    for tab_index in range(self.tab_count):
      if tab_index in changed_tabs:
        tab_graph_data = self._tab_graph_data(tab_index, tab_data[tab_index])
        graph_data[tab_index] = tab_graph_data['graph_data']
        output[f'avgdisplay_{tab_index}'] = 'Mean: {}'.format(round(tab_graph_data['mean'], 2))
        output[f'stddisplay_{tab_index}'] = 'σ: {}'.format(round(tab_graph_data['std'], 2))
      else:
        output[f'avgdisplay_{tab_index}'] = tab_data[tab_index]['states']['avgdisplay']
        output[f'stddisplay_{tab_index}'] = tab_data[tab_index]['states']['stddisplay']

    max_len = max(max([len(x.get('x', [])) for x in graph_data]), 20)
    output['damage_graph'] = self.graph_layout_generator.figure_template(graph_data, max_len)
    return output

  def _tab_graph_data(self, tab_index, data):
    tab_pmfs = []
    tab_data = data['inputs']
    tab_enabled = tab_data.get('enabled') == 'enabled'
    for weapon_index in range(self.weapon_count):
      weapon_data = data['weapons'][weapon_index]['inputs']
      weapon_enabled = weapon_data.get('weaponenabled') == 'enabled'
      if tab_enabled and weapon_enabled:
        tab_pmfs.append(self.compute_controller.compute(**tab_data, **weapon_data))
    tab_pmf = PMF.convolve_many(tab_pmfs)
    values = tab_pmf.cumulative().trim_tail().values
    if len(values) > 1:
      graph_data = {
        'x': [i for i, x in enumerate(values)],
        'y': [100*x for i, x in enumerate(values)],
        'name': tab_data.get('tabname'),
      }
    else:
      graph_data = {}
    return {
      'graph_data': graph_data,
      'mean': tab_pmf.mean(),
      'std': tab_pmf.std(),
    }

  def _tabs_changed(self):
    ctx = dash.callback_context
    if not ctx:
      return list(range(TAB_COUNT))
    tabs = []
    for trigger in ctx.triggered:
      match = re.match(r'(?P<input_name>[^_]+)_(?P<tab>\d+)(_(?P<weapon>\d+))?', trigger['prop_id'])
      if match:
        tabs.append(int(match.groupdict().get('tab')))
    return list(set(tabs))


class StaticGraphCallbackController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.graph_layout_generator = GraphLayout()
    self.compute_controller = ComputeController()
    self.url_minify = URLMinify(self.tab_count)

  def setup_callbacks(self):
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

  def update_static_graph(self, graph_args):
    title = graph_args.get(-1, {}).get('title')
    if not graph_args:
      return self.graph_layout_generator.figure_template()
    graph_data = []
    for tab_index in [x for x in sorted(graph_args.keys()) if x != -1]:
      data = self.compute_controller.compute(
        **graph_args[tab_index],
        existing_data=graph_args,
        re_render=True,
        tab_index=tab_index,
      )
      graph_data.append(data.get('graph_data'))
    max_len = max(max([len(x.get('x', [])) for x in graph_data]), 20)
    return self.graph_layout_generator.figure_template(graph_data, max_len, title)

  def parse_static_graph_args(self, graph_args):
    parsed_args = {}
    for key, value in graph_args.items():
      match = re.match(r'(?P<sub_key>.+)_(?P<tab_index>\d+)', key)
      if match:
        sub_key = match.groupdict().get('sub_key')
        tab_index = int(match.groupdict().get('tab_index'))
        if sub_key in ['shot_mods', 'hit_mods','wound_mods', 'save_mods', 'damage_mods']:
          value = value.split(',')
        if tab_index in parsed_args:
          parsed_args[tab_index][sub_key] = value
        else:
          parsed_args[tab_index] = {sub_key: value}
      else:
        if -1 in parsed_args:
          parsed_args[-1][key] = value
        else:
          parsed_args[-1] = {key: value}
    return parsed_args


class InputsCallbackController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def setup_callbacks(self):
    for tab_index in range(self.tab_count):
      self._setup_input_tab_callback(tab_index)

  def _setup_input_tab_callback(self, tab_index):
    # self.disable_callback(tab_index)
    self._tabname_callback(tab_index)
    self._setup_weaponname_callback(tab_index)

  def _setup_weaponname_callback(self, tab_index):
    for weapon_index in range(self.weapon_count):
      self._weaponname_callback(tab_index, weapon_index)

  def _tabname_callback(self, tab_index):
    @self.app.callback(
      Output(f'tab_{tab_index}', 'label'),
      [Input(f'tabname_{tab_index}', 'value')],
    )
    def update_tab_name(value):
        return value if len(value) > 2 else 'Profile'

  def _weaponname_callback(self, tab_index, weapon_index):
    @self.app.callback(
      Output(f'weapontab_{tab_index}_{weapon_index}', 'label'),
      [
        Input(f'weaponname_{tab_index}_{weapon_index}', 'value'),
        Input(f'weaponenabled_{tab_index}_{weapon_index}', 'value'),
      ],
    )
    def update_tab_name(value, enabled):
        value = value if len(value) > 2 else 'Weapon'
        if enabled == 'enabled':
          value = f'▪️ {value}'
        else:
          value = f'▫️ {value}'
        return value



class LinkCallbackController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.input_generator = InputGenerator()
    self.url_minify = URLMinify(self.tab_count)

  def setup_callbacks(self):
    mapper = CallbackMapper(
      outputs={'permalink': 'href'},
      inputs=self.input_generator.graph_inputs(self.tab_count, self.weapon_count),
    )
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def static_graph_callback(*args):
      tab_data = mapper.input_to_kwargs_by_tab(args, self.tab_count, self.weapon_count)
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



class CallbackController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count

    self.url_callback_controller = URLCallbackController(
      self.app,
      self.tab_count,
      self.weapon_count
    )

    self.graph_callback_controller = GraphCallbackController(
      self.app,
      self.tab_count,
      self.weapon_count
    )

    self.static_graph_callback_controller = StaticGraphCallbackController(
      self.app,
      self.tab_count,
      self.weapon_count
    )

    self.inputs_callback_controller = InputsCallbackController(
      self.app,
      self.tab_count,
      self.weapon_count
    )

    self.link_callback_controller = LinkCallbackController(
      self.app,
      self.tab_count,
      self.weapon_count
    )

  def setup_callbacks(self):
    self.url_callback_controller.setup_callbacks()
    self.graph_callback_controller.setup_callbacks()
    self.static_graph_callback_controller.setup_callbacks()
    self.inputs_callback_controller.setup_callbacks()
    self.link_callback_controller.setup_callbacks()




