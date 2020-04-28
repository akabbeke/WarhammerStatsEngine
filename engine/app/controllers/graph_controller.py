from collections import defaultdict

import re

import dash
import dash_core_components as dcc
import dash_html_components as html

from urllib.parse import urlparse, parse_qsl, urlencode

from flask import request
from dash.dependencies import Input, Output, State

from ...constants import TAB_COUNT, GA_TRACKING_ID, TAB_COLOURS, DEFAULT_GRAPH_PLOTS

from ..layout import GraphLayout, Layout

from ..util import ComputeController, URLMinify, InputGenerator

from ...stats.pmf import PMF

from .util import CallbackMapper, mapped_callback, track_event, recurse_default, chunks



class GraphController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.input_generator = InputGenerator(self.tab_count, self.weapon_count)
    self.graph_layout_generator = GraphLayout()
    self.compute_controller = ComputeController()
    self._subplot_names = {0: 'damage', 1: 'drones', 2: 'self'}

  def setup_callbacks(self):
    @mapped_callback(
      app=self.app,
      outputs=self._graph_updates(),
      inputs=self.input_generator.graph_inputs(),
      states=self._graph_updates(),
    )
    def _(*args):
      track_event(
        category='Render',
        action='Interactive',
        label=self._prop_change(),
      )
      return self._update_graph(*args)

  def _graph_updates(self):
    return {
      **{'damage_graph': 'figure'},

      **{f'avgdisplay_{i}': 'value' for i in range(self.tab_count)},
      **{f'stddisplay_{i}': 'value' for i in range(self.tab_count)},

      **{f'wepavgdisplay_{i}_{j}': 'value' for i in range(self.tab_count) for j in range(self.weapon_count)},
      **{f'wepstddisplay_{i}_{j}': 'value' for i in range(self.tab_count) for j in range(self.weapon_count)},
    }

  def _group_plot_data(self, current_plot_data):
    return {i: self._named_plot_data(x) for i, x in enumerate(chunks(current_plot_data, len(self._subplot_names)))}

  def _named_plot_data(self, data):
    return {self._subplot_names[i]: data[i] for i in range(len(self._subplot_names))}

  def _flatten_plot_data(self, data):
    flat = []
    for i in range(self.tab_count):
      flat += [data[i][self._subplot_names[j]] for j in range(len(self._subplot_names))]
    return flat

  def _update_graph(self, callback):
    output = {}
    current_plot_data = callback.global_states['damage_graph']['data']

    changed_tabs = self._tabs_changed(current_plot_data)

    grouped_plot_data = self._group_plot_data(current_plot_data)

    for tab_id in range(self.tab_count):
      if tab_id in changed_tabs:
        new_data = self._tab_graph_data(tab_id, callback)
        grouped_plot_data[tab_id] = new_data['graphs']
        output.update(self.tab_output(tab_id, new_data, callback))
      else:
        output.update(self.cached_tab_output(tab_id, callback))

    for tab_id in range(self.tab_count):
      pass

    flattened_plot_data =self._flatten_plot_data(grouped_plot_data)

    max_len = max(max([len(x.get('x', [])) for x in flattened_plot_data]), 0)
    output['damage_graph'] = self.graph_layout_generator.figure_template(
      flattened_plot_data,
      max_len,
      top=10
    )
    callback.set_outputs(**output)
    return callback

  def tab_output(self, tab_id, comp_data, callback):
    tab_data = comp_data
    if callback.tab_inputs[tab_id].get('enabled') == 'enabled':
      return self.enabled_tab_output(tab_id, tab_data)
    else:
      return self.disabled_tab_output(tab_id)

  def cached_tab_output(self, tab_id, callback):
    output = {}
    output[f'avgdisplay_{tab_id}'] = callback.tab_states[tab_id][f'avgdisplay']
    output[f'stddisplay_{tab_id}'] = callback.tab_states[tab_id][f'stddisplay']
    for weapon_id in range(self.weapon_count):
      weapon_state = callback.tab_states[tab_id]['weapons'][weapon_id]
      output[f'wepavgdisplay_{tab_id}_{weapon_id}'] = weapon_state[f'wepavgdisplay']
      output[f'wepstddisplay_{tab_id}_{weapon_id}'] = weapon_state[f'wepstddisplay']
    return output

  def metadata_output(self, tab_id, enabled, mean=None, std=None):
    return {
      f'avgdisplay_{tab_id}': '{}'.format(round(mean, 2)) if enabled else 'Tab disabled',
      f'stddisplay_{tab_id}': '{}'.format(round(std, 2)) if enabled else 'Tab disabled',
    }

  def weapon_metadata_output(self, tab_id, weapon_id, enabled, wep_enabled, mean=None, std=None):
    if enabled:
      if wep_enabled:
        return {
          f'wepavgdisplay_{tab_id}_{weapon_id}': '{}'.format(round(mean, 2)),
          f'wepstddisplay_{tab_id}_{weapon_id}': '{}'.format(round(std, 2)),
        }
      else:
        return {
          f'wepavgdisplay_{tab_id}_{weapon_id}': 'Weapon disabled',
          f'wepstddisplay_{tab_id}_{weapon_id}': 'Weapon disabled',
        }
    else:
      return {
        f'wepavgdisplay_{tab_id}_{weapon_id}': 'Tab disabled',
        f'wepstddisplay_{tab_id}_{weapon_id}': 'Tab disabled',
      }

  def enabled_tab_output(self, tab_id, tab_data):
    output = {}
    tab_metadata = tab_data['metadata']
    output = self.metadata_output(tab_id, True, tab_metadata['mean'], tab_metadata['std'])
    for weapon_id in range(self.weapon_count):
      weapon_metadata = tab_data['metadata']['weapon_metadata'][weapon_id]
      output.update(self.weapon_metadata_output(
        tab_id,
        weapon_id,
        True,
        weapon_metadata['mean'] > -1,
        mean=weapon_metadata['mean'],
        std=weapon_metadata['std'],
      ))
    return output

  def disabled_tab_output(self, tab_id):
    output = self.metadata_output(tab_id, False, 0, 0)
    for weapon_id in range(self.weapon_count):
      output.update(self.weapon_metadata_output(tab_id, weapon_id, False, False, 0, 0))
    return output

  def get_damage_plot(self, tab_data, tab_results, colour):
    damage_pmfs = [x.damage_with_mortals for x in tab_results]
    damage_values = PMF.convolve_many(damage_pmfs).cumulative().trim_tail().values
    if len(damage_values) > 1:
      return {
        'x': [i for i, x in enumerate(damage_values)],
        'y': [100*x for i, x in enumerate(damage_values)],
        'name': tab_data.get('tabname'),
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
        'name': 'Drone DMG',
        'line': {'dash': 'dash', 'color': colour},
        'legendgroup': tab_data.get('tabname')
      }
    else:
      return {}

  def get_self_damage_plot(self, tab_data, tab_results, colour):
    damage_pmfs = [x.self_wound for x in tab_results]
    damage_values = PMF.convolve_many(damage_pmfs).cumulative().trim_tail().values

    if len(damage_values) > 1:
      return {
        'x': [i for i, x in enumerate(damage_values)],
        'y': [100*x for i, x in enumerate(damage_values)],
        'name': 'Self DMG',
        'line': {'dash': 'dot', 'color': colour},
        'legendgroup': tab_data.get('tabname')
      }
    else:
      return {}

  def _tab_graph_data(self, tab_id, callback):
    tab_results = []
    tab_inputs = callback.tab_inputs[tab_id]

    weapon_metadata = {}

    tab_enabled = tab_inputs.get('enabled') == 'enabled'

    for weapon_id in range(self.weapon_count):
      weapon_inputs = tab_inputs['weapons'].get(weapon_id)
      if tab_enabled and weapon_inputs and weapon_inputs.get('weaponenabled') == 'enabled':
        results = self.compute_controller.compute(**tab_inputs, **weapon_inputs)
        tab_results.append(results)
        weapon_metadata[weapon_id] = {
          'mean': results.damage_with_mortals.mean(),
          'std': results.damage_with_mortals.std(),
        }
      else:
        weapon_metadata[weapon_id] = {
          'mean': -1,
          'std': -1,
        }

    tab_pmf = PMF.convolve_many([x.damage_with_mortals for x in tab_results])
    colour = TAB_COLOURS[tab_id]

    return {
      'graphs': {
        'damage': self.get_damage_plot(tab_inputs, tab_results, colour),
        'drones': self.get_drone_plot(tab_inputs, tab_results, colour),
        'self': self.get_self_damage_plot(tab_inputs, tab_results, colour),
      },
      'metadata': {
        'mean': tab_pmf.mean(),
        'std': tab_pmf.std(),
        'weapon_metadata': weapon_metadata,
      },
    }

  def _prop_change(self):
    ctx = dash.callback_context
    if not ctx:
      return None
    return ctx.triggered[0]['prop_id']

  def _tabs_changed(self, graph_data):
    if graph_data == DEFAULT_GRAPH_PLOTS:
      return list(range(self.tab_count))
    else:
      return self._get_tabs_changed()

  def _get_tabs_changed(self):
    ctx = dash.callback_context
    if not ctx:
      return list(range(TAB_COUNT))
    tabs = []
    for trigger in ctx.triggered:
      match = re.match(r'(?P<input_name>[^_]+)_(?P<tab>\d+)(_(?P<weapon>\d+))?', trigger['prop_id'])
      if match:
        tabs.append(int(match.groupdict().get('tab')))
    return list(set(tabs))
