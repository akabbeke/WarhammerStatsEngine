from collections import defaultdict

import re

import dash
import dash_core_components as dcc
import dash_html_components as html

from urllib.parse import urlparse, parse_qsl, urlencode

from flask import request
from dash.dependencies import Input, Output, State

from ...constants import TAB_COUNT, GA_TRACKING_ID

from ..layout import GraphLayout, Layout

from ..util import ComputeController, URLMinify, InputGenerator

from ...stats.pmf import PMF

from .util import CallbackMapper, track_event, recurse_default

class GraphController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.input_generator = InputGenerator(self.tab_count, self.weapon_count)
    self.graph_layout_generator = GraphLayout()
    self.compute_controller = ComputeController()

  def setup_callbacks(self):
    mapper = CallbackMapper(
      outputs=self._graph_updates(),
      inputs=self.input_generator.graph_inputs(),
      states=self._graph_updates(),
    )
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def _(*args):
      track_event(
        category='Render',
        action='Interactive',
        label=self._prop_change(),
      )
      tab_data = mapper.input_to_kwargs_by_tab(args, self.tab_count, self.weapon_count)
      result_dict = self._update_graph(tab_data)
      return mapper.dict_to_output(result_dict)

  def _graph_updates(self):
    return {
      **{'damage_graph': 'figure'},

      **{f'avgdisplay_{i}': 'value' for i in range(self.tab_count)},
      **{f'stddisplay_{i}': 'value' for i in range(self.tab_count)},

      **{f'wepavgdisplay_{i}_{j}': 'value' for i in range(self.tab_count) for j in range(self.weapon_count)},
      **{f'wepstddisplay_{i}_{j}': 'value' for i in range(self.tab_count) for j in range(self.weapon_count)},

      # **{f'weaponname_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'strength_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'ap_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'ws_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'shots_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'damage_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},

      # **{f'shotmods_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'hitmods_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'woundmods_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'savemods_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'fnpmods_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
      # **{f'damagemods_{i}_{j}': 'disabled' for i in range(self.tab_count) for j in range(self.weapon_count)},
    }

  def _update_graph(self, tab_data):
    # TODO: refactor this whole mess
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
        if tab_data[tab_index]['inputs'].get('enabled') == 'enabled':
          output[f'avgdisplay_{tab_index}'] = '{}'.format(round(tab_graph_data['mean'], 2))
          output[f'stddisplay_{tab_index}'] = '{}'.format(round(tab_graph_data['std'], 2))
          for weapon_index in range(self.weapon_count):
            wep_mean = tab_graph_data['weapon_data'][weapon_index]['mean']
            wep_std = tab_graph_data['weapon_data'][weapon_index]['std']
            output[f'wepavgdisplay_{tab_index}_{weapon_index}'] = '{}'.format(round(wep_mean, 2)) if wep_mean > -1 else 'Weapon disabled'
            output[f'wepstddisplay_{tab_index}_{weapon_index}'] = '{}'.format(round(wep_std, 2)) if wep_std > -1 else 'Weapon disabled'
        else:
          output[f'avgdisplay_{tab_index}'] = 'Tab disabled'
          output[f'stddisplay_{tab_index}'] = 'Tab disabled'
          for weapon_index in range(self.weapon_count):
            output[f'wepavgdisplay_{tab_index}_{weapon_index}'] = 'Tab disabled'
            output[f'wepstddisplay_{tab_index}_{weapon_index}'] = 'Tab disabled'
      else:

        output[f'avgdisplay_{tab_index}'] = tab_data[tab_index]['states']['avgdisplay']
        output[f'stddisplay_{tab_index}'] = tab_data[tab_index]['states']['stddisplay']
        for weapon_index in range(self.weapon_count):
          wep_state = tab_data[tab_index]['weapons'][weapon_index]['states']
          output[f'wepavgdisplay_{tab_index}_{weapon_index}'] = wep_state['wepavgdisplay']
          output[f'wepstddisplay_{tab_index}_{weapon_index}'] = wep_state['wepstddisplay']

    max_len = max(max([len(x.get('x', [])) for x in graph_data]), 0)
    output['damage_graph'] = self.graph_layout_generator.figure_template(graph_data, max_len, top=10)
    # output.update(self._tab_enabled(tab_data))
    return output

  def _tab_enabled(self, graph_data):
    data = {}
    for i in range(self.tab_count):
      tab_enabled = graph_data[i]['inputs']['enabled'] == 'enabled'
      for j in range(self.weapon_count):
        weapon_enabled = graph_data[i]['weapons'][j]['inputs']['weaponenabled'] == 'enabled'
        input_disabled = not (tab_enabled and weapon_enabled)
        data.update({
          f'weaponname_{i}_{j}': input_disabled,
          f'strength_{i}_{j}': input_disabled,
          f'ap_{i}_{j}': input_disabled,
          f'ws_{i}_{j}': input_disabled,
          f'shots_{i}_{j}': input_disabled,
          f'damage_{i}_{j}': input_disabled,
          f'shotmods_{i}_{j}': input_disabled,
          f'hitmods_{i}_{j}': input_disabled,
          f'woundmods_{i}_{j}': input_disabled,
          f'savemods_{i}_{j}': input_disabled,
          f'fnpmods_{i}_{j}': input_disabled,
          f'damagemods_{i}_{j}': input_disabled,
        })
    return data

  def _tab_graph_data(self, tab_index, data):
    tab_pmfs = []
    tab_data = data['inputs']
    tab_enabled = tab_data.get('enabled') == 'enabled'
    weapon_mean = {}
    for weapon_index in range(self.weapon_count):
      weapon_data = data['weapons'][weapon_index]['inputs']
      weapon_enabled = weapon_data.get('weaponenabled') == 'enabled'
      if tab_enabled and weapon_enabled:
        weapon_pmf = self.compute_controller.compute(**tab_data, **weapon_data)
        tab_pmfs.append(weapon_pmf)
        weapon_mean[weapon_index] = {
          'mean': weapon_pmf.mean(),
          'std': weapon_pmf.std(),
        }
      else:
        weapon_mean[weapon_index] = {
          'mean': -1,
          'std': -1,
        }

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
      'weapon_data': weapon_mean,
    }

  def _prop_change(self):
    ctx = dash.callback_context
    if not ctx:
      return None
    return ctx.triggered[0]['prop_id']

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
