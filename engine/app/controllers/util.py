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

from ...constants import TAB_COUNT, GA_TRACKING_ID
from ...stats.pmf import PMF


def recurse_default():
  return defaultdict(recurse_default)

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



