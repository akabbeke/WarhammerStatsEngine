from collections import defaultdict

import re
import dash_core_components as dcc
import dash_html_components as html

from urllib.parse import urlparse, parse_qsl, urlencode

from flask import request
from dash.dependencies import Input, Output, State

from ..layout import GraphLayout, Layout

from ..util import ComputeController, URLMinify, InputGenerator

from ...stats.pmf import PMF

from .util import CallbackMapper, track_event, recurse_default

class StaticController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.graph_layout_generator = GraphLayout()
    self.compute_controller = ComputeController()
    self.url_minify = URLMinify(self.tab_count, self.weapon_count)

  def setup_callbacks(self):
    mapper = CallbackMapper(
      outputs={'static_graph_debug': 'children', 'static_damage_graph': 'figure'},
      inputs={'url': 'href', 'page-2-radios': 'value'},
    )
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def _(*args):
      track_event(
        category='Render',
        action='Static',
      )
      tab_data = mapper.input_to_kwargs(args)
      url_args = self._parse_url_params(tab_data['inputs']['url'])
      graph_args = self._parse_static_graph_args(url_args)
      output = {
        'static_graph_debug': str(graph_args),
        'static_damage_graph': self.update_static_graph(graph_args),
        }
      return mapper.dict_to_output(output)

  def _parse_url_params(self, url):
    parse_result = urlparse(url)
    params = parse_qsl(parse_result.query)
    state = dict(params)
    max_map = self.url_minify.to_max()
    return {max_map.get(x, x):y for x,y in state.items()}

  def _parse_static_graph_args(self, inputs):
    parsed_inputs = recurse_default()
    for raw_input_name, value in inputs.items():
      match = re.match(r'(?P<input_name>[^_]+)_(?P<tab>\d+)(_(?P<weapon>\d+))?', raw_input_name)
      if match:
        input_name = match.groupdict().get('input_name')
        tab = match.groupdict().get('tab')
        weapon = match.groupdict().get('weapon')
        if input_name in ['shotmods', 'hitmods','woundmods', 'savemods', 'fnpmods', 'damagemods']:
          value = value.split(',')
        if weapon:
          parsed_inputs[int(tab)]['weapons'][int(weapon)]['inputs'][input_name] = value
        else:
          parsed_inputs[int(tab)]['inputs'][input_name] = value
      else:
        parsed_inputs[-1]['inputs'][raw_input_name] = value
    return self.default_to_regular(parsed_inputs)

  def default_to_regular(self, d):
    if isinstance(d, defaultdict):
      d = {k: self.default_to_regular(v) for k, v in d.items()}
    return d

  def update_static_graph(self, graph_args):
    title = graph_args.get(-1, {'inputs': {}})['inputs'].get('title')
    if not graph_args:
      return self.graph_layout_generator.figure_template()
    graph_data = []
    for tab_index in [x for x in sorted(graph_args.keys()) if x != -1]:
      tab_pmfs = []
      tab_data = graph_args[tab_index]
      if tab_data.get('weapons'):
        for weapon_data in tab_data['weapons'].values():
          data = self.compute_controller.compute(**tab_data['inputs'], **weapon_data['inputs'])
          tab_pmfs.append(data)
      tab_pmf = PMF.convolve_many(tab_pmfs)
      values = tab_pmf.cumulative().trim_tail().values
      if len(values) > 1:
        tab_data = {
          'x': [i for i, x in enumerate(values)],
          'y': [100*x for i, x in enumerate(values)],
          'name': tab_data['inputs'].get('tabname'),
        }
      else:
        tab_data = {}
      graph_data.append(tab_data)
    max_len = max(max([len(x.get('x', [])) for x in graph_data]), 0)
    return self.graph_layout_generator.figure_template(graph_data, max_len, title)
