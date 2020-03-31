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

class InputsController(object):
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
      [
        Input(f'tabname_{tab_index}', 'value'),
        Input(f'enabled_{tab_index}', 'value'),
      ],
    )
    def _(value, enabled):
      value = value if len(value) > 2 else 'Profile'
      if enabled == 'enabled':
        value = f'▪️ {value}'
      else:
        value = f'▫️ {value}'
      return value

  def _weaponname_callback(self, tab_index, weapon_index):
    @self.app.callback(
      Output(f'weapontab_{tab_index}_{weapon_index}', 'label'),
      [
        Input(f'weaponname_{tab_index}_{weapon_index}', 'value'),
        Input(f'weaponenabled_{tab_index}_{weapon_index}', 'value'),
      ],
    )
    def _(value, enabled):
      value = value if len(value) > 2 else 'Weapon'
      if enabled == 'enabled':
        value = f'▪️ {value}'
      else:
        value = f'▫️ {value}'
      return value
