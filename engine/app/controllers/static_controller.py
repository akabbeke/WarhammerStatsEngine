from collections import defaultdict

import re
import dash_core_components as dcc
import dash_html_components as html

from urllib.parse import urlparse, parse_qsl, urlencode

from flask import request
from dash.dependencies import Input, Output, State

from ..layout import GraphLayout, Layout

from ...constants import TAB_COLOURS


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
      outputs={
        'static_graph_debug': 'children',
        'static_damage_graph': 'figure',
        **self.avg_updates(),
      },
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
      static_damage_graph, tab_metrics = self.update_static_graph(graph_args)
      output = {
        'static_graph_debug': str(graph_args),
        'static_damage_graph': static_damage_graph,
        **self._update_avg(tab_metrics)
      }
      return mapper.dict_to_output(output)

  def _update_avg(self, tab_metrics):
    updates = {}
    for i in range(self.tab_count):
      updates[f'stattabname_{i}'] = tab_metrics.get(i, {}).get('tab_name', 'n/a')
      updates[f'statavgdisplay_{i}'] = tab_metrics.get(i, {}).get('tab_means', 'n/a')
      updates[f'statstddisplay_{i}'] = tab_metrics.get(i, {}).get('tab_stds', 'n/a')
    return updates

  def avg_updates(self):
    updates = {}
    for i in range(self.tab_count):
      updates[f'stattabname_{i}'] = 'value'
      updates[f'statavgdisplay_{i}'] = 'value'
      updates[f'statstddisplay_{i}'] = 'value'
    return updates


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

  def get_tab_results(self, tab_data):
    tab_results = []
    if tab_data.get('weapons'):
      for weapon_data in tab_data['weapons'].values():
        results = self.compute_controller.compute(**tab_data['inputs'], **weapon_data['inputs'])
        tab_results.append(results)
    return tab_results

  def get_damage_plot(self, tab_data, tab_results, colour):
    damage_pmfs = [x.damage_with_mortals for x in tab_results]
    damage_values = PMF.convolve_many(damage_pmfs).cumulative().trim_tail().values

    if len(damage_values) > 1:
      return {
        'x': [i for i, x in enumerate(damage_values)],
        'y': [100*x for i, x in enumerate(damage_values)],
        'name': tab_data['inputs'].get('tabname'),
        'line': {'color': colour},
        'legendgroup': tab_data.get('tabname')
      }
    else:
      return {}

  def get_drone_plot(self, tab_data, tab_results, colour):
    damage_pmfs = [x.drone_wound for x in tab_results]
    damage_values = PMF.convolve_many(damage_pmfs).cumulative().trim_tail().values

    if len(damage_values) > 1:
      return {
        'x': [i for i, x in enumerate(damage_values)],
        'y': [100*x for i, x in enumerate(damage_values)],
        'name': 'Drone',
        'line': {'dash': 'dash', 'color': colour},
        'legendgroup': tab_data.get('tabname')
      }
    else:
      return {}

  def update_static_graph(self, graph_args):
    title = graph_args.get(-1, {'inputs': {}})['inputs'].get('title')
    if not graph_args:
      return self.graph_layout_generator.figure_template()
    graph_data = []
    tab_metrics = {}
    for tab_id in [x for x in sorted(graph_args.keys()) if x != -1]:
      tab_data = graph_args[tab_id]
      tab_results = self.get_tab_results(tab_data)

      colour = TAB_COLOURS[tab_id]

      [
        self.get_damage_plot(tab_data, results, colour),
        self.get_drone_plot(tab_data, results, colour),
      ]

      tab_pmf = PMF.convolve_many(tab_pmfs)
      values = tab_pmf.cumulative().trim_tail().values
      if len(values) > 1:
        tab_graph_data = {
          'x': [i for i, x in enumerate(values)],
          'y': [100*x for i, x in enumerate(values)],
          'name': tab_data['inputs'].get('tabname'),
        }
        tab_name = tab_data['inputs'].get('tabname')
      else:
        tab_name = 'n/a'
        tab_data = {}
      graph_data.append(tab_graph_data)
      tab_metrics[tab_id] = {
        'tab_name': tab_name,
        'tab_means': tab_pmf.mean(),
        'tab_stds': tab_pmf.std(),
      }
    max_len = max(max([len(x.get('x', [])) for x in graph_data]), 0)
    return self.graph_layout_generator.figure_template(graph_data, max_len, title), tab_metrics
