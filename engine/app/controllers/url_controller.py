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

from .util import CallbackMapper, track_event, recurse_default

class URLController(object):
  def __init__(self, app, tab_count, weapon_count):
    self.app = app
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.layout_generator = Layout(self.tab_count, self.weapon_count)

  def setup_callbacks(self):
    mapper = CallbackMapper(outputs={'page_content': 'children'}, inputs={'url': 'pathname'})
    @self.app.callback(mapper.outputs, mapper.inputs,mapper.states)
    def _(pathname):
      result_dict = {}
      if pathname == '/':
        result_dict['page_content'] = self.layout_generator.base_layout()
      elif pathname == '/static':
        result_dict['page_content'] = self.layout_generator.static_layout()
      elif pathname == '/embed':
        result_dict['page_content'] = self.layout_generator.embed_layout()
      return mapper.dict_to_output(result_dict)