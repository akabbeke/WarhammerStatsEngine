from collections import defaultdict

import re
import dash_core_components as dcc
import dash_html_components as html

from urllib.parse import urlparse, parse_qsl, urlencode

from flask import request
from dash.dependencies import Input, Output, State

from ..layout import GraphLayout, Layout

from ...constants import TAB_COLOURS, DEFAULT_GRAPH_PLOTS


from ..util import ComputeController, URLMinify, InputGenerator

from ...stats.pmf import PMF

from .util import CallbackMapper, track_event, recurse_default, mapped_callback
from .graph_controller import GraphController

class StaticController(GraphController):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.url_minify = URLMinify(self.tab_count, self.weapon_count)

  def setup_callbacks(self):
    @mapped_callback(
      app=self.app,
      outputs={
        'static_graph_debug': 'children',
        'static_damage_graph': 'figure',
        **self.avg_updates(),
      },
      inputs={'url': 'href', 'page-2-radios': 'value'},
    )
    def _(callback):
      track_event(category='Render', action='Static')
      return self.update_static_graph(callback)

  def _update_avg(self, tab_id, name, mean, std):
    return {
      f'stattabname_{tab_id}': name,
      f'statavgdisplay_{tab_id}': mean,
      f'statstddisplay_{tab_id}': std,
    }

  def avg_updates(self):
    updates = {}
    for i in range(self.tab_count):
      updates[f'stattabname_{i}'] = 'value'
      updates[f'statavgdisplay_{i}'] = 'value'
      updates[f'statstddisplay_{i}'] = 'value'
    return updates


  def update_static_graph(self, callback):
    # if not graph_args:
    #   return self.graph_layout_generator.figure_template()
    output = {}
    metadata = {}
    title = callback.global_inputs.get('title')

    callback.update_from_url()

    grouped_plot_data = self._group_plot_data(DEFAULT_GRAPH_PLOTS)

    for tab_id in range(self.tab_count):
      if callback.tab_inputs[tab_id]:
        new_data = self._tab_graph_data(tab_id, callback)
        print(new_data['graphs'])
        grouped_plot_data[tab_id] = new_data['graphs']
        output.update(self._update_avg(
          tab_id,
          callback.tab_inputs.get(tab_id, {}).get('tabname', 'n/a'),
          new_data['metadata']['mean'],
          new_data['metadata']['std'],
        ))

    flattened_plot_data =self._flatten_plot_data(grouped_plot_data)
    max_len = max(max([len(x.get('x', [])) for x in flattened_plot_data]), 0)
    output['static_graph_debug'] = ''
    output['static_damage_graph'] = self.graph_layout_generator.figure_template(
      flattened_plot_data,
      max_len,
      title=title,
      top=10
    )
    callback.set_outputs(**output)
    return callback
