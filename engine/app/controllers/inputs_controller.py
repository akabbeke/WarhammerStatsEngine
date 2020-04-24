from collections import defaultdict

import re
import dash_core_components as dcc
import dash_html_components as html

from urllib.parse import urlparse, parse_qsl, urlencode

from flask import request
from dash import callback_context
from dash.dependencies import Input, Output, State

from ..layout import GraphLayout, Layout

from ..util import ComputeController, URLMinify, InputGenerator

from ...stats.pmf import PMF

from .util import CallbackMapper, track_event, recurse_default

class InputsController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def setup_callbacks(self):
    for tab_id in range(self.tab_count):
      self._setup_input_tab_callback(tab_id)

  def _setup_input_tab_callback(self, tab_id):
    self._setup_preset_callback(tab_id)
    self._tabname_callback(tab_id)
    self._setup_weaponname_callback(tab_id)

  def _setup_weaponname_callback(self, tab_id):
    for weapon_id in range(self.weapon_count):
      self._weaponname_callback(tab_id, weapon_id)

  def _setup_preset_callback(self, tab_id):
    @self.app.callback(
      output=[
        Output(f'toughness_{tab_id}', 'value'),
        Output(f'save_{tab_id}', 'value'),
        Output(f'invuln_{tab_id}', 'value'),
        Output(f'fnp_{tab_id}', 'value'),
        Output(f'wounds_{tab_id}', 'value'),
      ],
      inputs=[
        Input(f'guardsman_{tab_id}', 'n_clicks'),
        Input(f'ork_boy_{tab_id}', 'n_clicks'),
        Input(f'shield_drone_{tab_id}', 'n_clicks'),
        Input(f'tactical_marine_{tab_id}', 'n_clicks'),
        Input(f'intercessor_{tab_id}', 'n_clicks'),
        Input(f'terminator_{tab_id}', 'n_clicks'),
        Input(f'crisis_suit_{tab_id}', 'n_clicks'),
        Input(f'custode_{tab_id}', 'n_clicks'),
        Input(f'rhino_{tab_id}', 'n_clicks'),
        Input(f'leman_russ_{tab_id}', 'n_clicks'),
        Input(f'knight_{tab_id}', 'n_clicks'),
      ],
    )
    def _(*args):
      # [toughness, +, ++, +++, wounds]
      if not callback_context:
        return [3,5,7,7,1]
      trigger = callback_context.triggered[0]['prop_id']
      if 'guardsman' in trigger:
        return [3,5,7,7,1]
      elif 'ork_boy' in trigger:
        return [4,6,7,7,1]
      elif 'shield_drone' in trigger:
        return [4,4,4,5,1]
      elif 'tactical_marine' in trigger:
        return [4,3,7,7,1]
      elif 'intercessor' in trigger:
        return [4,3,7,7,2]
      elif 'terminator' in trigger:
        return [4,3,4,7,2]
      elif 'crisis_suit' in trigger:
        return [5,3,7,7,3]
      elif 'custode' in trigger:
        return [5,2,3,7,3]
      elif 'rhino' in trigger:
        return [7,3,7,7,10]
      elif 'leman_russ' in trigger:
        return [8,3,7,7,12]
      elif 'knight' in trigger:
        return [8,3,5,7,24]

  def _tabname_callback(self, tab_id):
    @self.app.callback(
      Output(f'tab_{tab_id}', 'label'),
      [
        Input(f'tabname_{tab_id}', 'value'),
        Input(f'enabled_{tab_id}', 'value'),
      ],
    )
    def _(value, enabled):
      value = value if len(value) > 2 else 'Profile'
      if enabled == 'enabled':
        value = f'▪️ {value}'
      else:
        value = f'▫️ {value}'
      return value

  def _weaponname_callback(self, tab_id, weapon_id):
    @self.app.callback(
      Output(f'weapontab_{tab_id}_{weapon_id}', 'label'),
      [
        Input(f'weaponname_{tab_id}_{weapon_id}', 'value'),
        Input(f'weaponenabled_{tab_id}_{weapon_id}', 'value'),
      ],
    )
    def _(value, enabled):
      value = value if len(value) > 2 else 'Weapon'
      if enabled == 'enabled':
        value = f'▪️ {value}'
      else:
        value = f'▫️ {value}'
      return value
