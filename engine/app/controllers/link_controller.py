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

class LinkController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.input_generator = InputGenerator(self.tab_count, self.weapon_count)
    self.url_minify = URLMinify(self.tab_count, self.weapon_count)

  def setup_callbacks(self):
    mapper = CallbackMapper(
      outputs={'permalink': 'href'},
      inputs=self.input_generator.graph_inputs(),
    )
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def _(*args):
      tab_data = mapper.input_to_kwargs_by_tab(args, self.tab_count, self.weapon_count)
      result_dict = {'permalink': self.convert_args_to_url(tab_data)}
      return mapper.dict_to_output(result_dict)

  def convert_args_to_url(self, input_data):
    url_args = {}
    for tab_id, tab_data in input_data.items():
      if tab_data['inputs'].get('enabled') == 'enabled':
        for key, value in tab_data['inputs'].items():
          url_args[f'{key}_{tab_id}'] = value
        for weapon_id, weapon_data in tab_data['weapons'].items():
          if weapon_data['inputs'].get('weaponenabled') == 'enabled':
            for key, value in weapon_data['inputs'].items():
              if key in ['shotmods', 'hitmods','woundmods', 'savemods', 'fnpmods', 'damagemods']:
                url_args[f'{key}_{tab_id}_{weapon_id}'] = ','.join(value or [])
              else:
                url_args[f'{key}_{tab_id}_{weapon_id}'] = value

    url_args.update(input_data[-1]['inputs'])
    min_map = self.url_minify.to_min()
    url_args = {min_map.get(x, x):y for x,y in url_args.items()}
    state = urlencode(url_args)
    return f'/static?{state}'
