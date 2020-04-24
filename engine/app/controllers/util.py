from collections import defaultdict

import hashlib

import dash
import dash_daq as daq
import re
import requests
import dash_core_components as dcc
import dash_html_components as html

from urllib.parse import urlparse, parse_qsl, urlencode

from flask import request
from dash.dependencies import Input, Output, State

from ..layout import GraphLayout, Layout

from ..util import ComputeController, URLMinify, InputGenerator

from ...constants import TAB_COUNT, WEAPON_COUNT, GA_TRACKING_ID
from ...stats.pmf import PMF


def recurse_default():
  return defaultdict(recurse_default)


def chunks(lst, n):
  """Yield successive n-sized chunks from lst."""
  for i in range(0, len(lst), n):
    yield lst[i:i + n]


def get_cid():
  try:
    _, _, left, right = request.cookies.get('_ga').split('.')
    return f'{left}.{right}'
  except:
    pass


def get_gid():
  try:
    _, _, left, right = request.cookies.get('_gid').split('.')
    return f'{left}.{right}'
  except:
    pass


def track_event(category, action, label=None, value=0):
  cid = get_cid()
  gid = get_gid()

  if not cid:
    return

  data = {
    'v': '1',  # API Version.
    'tid': 'UA-158827538-1',  # Tracking ID / Property ID.
    'cid': cid,
    't': 'event',  # Event hit type.
    'ec': category,  # Event category.
    'ea': action,  # Event action.
    'el': label,  # Event label.
    'ev': value,  # Event value, must be an integer
  }

  if gid:
    data['_gid'] = gid

  response = requests.post(
    'https://www.google-analytics.com/collect',
    headers={ "user-agent": "client" },
    data=data,
  )

  # If the request fails, this will raise a RequestException. Depending
  # on your application's needs, this may be a non-error and can be caught
  # by the caller.
  response.raise_for_status()

class CallbackMap(object):
  def __init__(self, raw_input, outputs_order, inputs_order, states_order):
    self._raw_input = raw_input
    self._outputs_order = outputs_order
    self._inputs_order = inputs_order
    self._states_order = states_order

    self._inputs = None
    self._tab_inputs = None
    self._global_inputs = None

    self._states = None
    self._tab_states = None
    self._global_states = None

    self._url_minify = None

    self._outputs = {}

  @property
  def inputs(self):
    if self._inputs is None:
      self._inputs = self._parse_inputs()
    return self._inputs

  @property
  def states(self):
    if self._states is None:
      self._states = self._parse_states()
    return self._states

  @property
  def tab_inputs(self):
    if self._tab_inputs is None:
      self._tab_inputs, self._global_inputs = self._parse_tab_inputs()
    return self._tab_inputs

  @property
  def tab_states(self):
    if self._tab_states is None:
      self._tab_states, self._global_states = self._parse_tab_states()
    return self._tab_states

  @property
  def global_inputs(self):
    if self._global_inputs is None:
      self._tab_inputs, self._global_inputs = self._parse_tab_inputs()
    return self._global_inputs

  @property
  def global_states(self):
    if self._global_states is None:
      self._tab_states, self._global_states = self._parse_tab_states()
    return self._global_states

  @property
  def outputs(self):
    return [self._outputs[k] for k in self._outputs_order]

  @property
  def url_minify(self):
    if self._url_minify is None:
      self._url_minify = URLMinify(TAB_COUNT, WEAPON_COUNT)
    return self._url_minify

  def update_from_url(self):
    url_args = self._parse_url_params()
    self.tab_inputs
    tab_fields, global_fields = self._parse_static_graph_args(url_args)
    self._tab_inputs.update(tab_fields)
    self.global_inputs.update(global_fields)


  def _parse_url_params(self):
    url = self.inputs['url']
    parse_result = urlparse(url)
    params = parse_qsl(parse_result.query)
    state = dict(params)
    print(state)
    max_map = self.url_minify.to_max()
    return {max_map.get(x, x): y for x,y in state.items()}

  def _parse_static_graph_args(self, inputs):
    global_fields = recurse_default()
    tab_fields = recurse_default()
    for raw_input_name, value in inputs.items():
      match = re.match(r'(?P<field_name>[^_]+)_(?P<tab_id>\d+)(_(?P<weapon_id>\d+))?', raw_input_name)
      if match:
        field_name = match.groupdict().get('field_name')
        tab_id = match.groupdict().get('tab_id')
        weapon_id = match.groupdict().get('weapon_id')
        if field_name in ['shotmods', 'hitmods','woundmods', 'savemods', 'fnpmods', 'damagemods']:
          value = value.split(',')
        if weapon_id:
          tab_fields[int(tab_id)]['weapons'][int(weapon_id)][field_name] = value
        else:
          tab_fields[int(tab_id)][field_name] = value
      else:
        global_fields[raw_input_name] = value
    return self.default_to_regular(tab_fields), self.default_to_regular(global_fields)

  def set_outputs(self, **kwargs):
    self._outputs.update(kwargs)

  def _parse_inputs(self):
    input_dict = {}
    for i, key in enumerate(self._inputs_order):
      input_dict[key] = self._raw_input[i]
    return input_dict

  def _parse_states(self):
    state_dict = {}
    for j, key in enumerate(self._states_order):
      state_dict[key] = self._raw_input[len(self._inputs_order) + j]
    return state_dict

  def _parse_tab_inputs(self):
    return self._parse_tab_fields(self.inputs)

  def _parse_tab_states(self):
    return self._parse_tab_fields(self.states)

  def default_to_regular(self, d):
    if isinstance(d, defaultdict):
        d = {k: self.default_to_regular(v) for k, v in d.items()}
    return d

  def _parse_tab_fields(self, fields=None):
    tab_fields = recurse_default()
    global_fields = recurse_default()
    for raw_input_name, value in fields.items():
      match = re.match(r'(?P<field_name>[^_]+)_(?P<tab_id>\d+)(_(?P<weapon_id>\d+))?', raw_input_name)
      if match:
        field_name = match.groupdict().get('field_name')
        tab_id = match.groupdict().get('tab_id')
        weapon_id = match.groupdict().get('weapon_id')
        if weapon_id:
          tab_fields[int(tab_id)]['weapons'][int(weapon_id)][field_name] = value
        else:
          tab_fields[int(tab_id)][field_name] = value
      else:
        global_fields[raw_input_name] = value
    return self.default_to_regular(tab_fields), self.default_to_regular(global_fields)


class mapped_callback(object):
  def __init__(self, app, outputs=None, inputs=None, states=None, tab_count=1, weapon_count=1):
    self._app = app

    self._outputs = outputs or {}
    self._outputs_order = sorted(self._outputs.keys())
    self._inputs = inputs or {}
    self._inputs_order = sorted(self._inputs.keys())
    self._states = states or {}
    self._states_order = sorted(self._states.keys())

    self._tab_count = tab_count,
    self._weapon_count = weapon_count,


  @property
  def outputs(self):
    return [Output(k, self._outputs[k]) for k in self._outputs_order]

  @property
  def inputs(self):
    return [Input(k, self._inputs[k]) for k in self._inputs_order]

  @property
  def states(self):
    return [State(k, self._states[k]) for k in self._states_order]

  def __call__(self, func):
    @self._app.callback(self.outputs, self.inputs, self.states)
    def callback(*args, **kwargs):
      return self.unmap(func(self.map(*args)))
    return callback

  def map(self, *args):
    return CallbackMap(
      raw_input = args,
      outputs_order = self._outputs_order,
      inputs_order = self._inputs_order,
      states_order = self._states_order,
    )

  def unmap(self, result):
    return result.outputs


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



