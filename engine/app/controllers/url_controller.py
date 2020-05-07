from dash import no_update

from .util import CallbackMapper
from ..layout import Layout


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
      # FIXME(kiciek): why on startup pathname = None ?
      result_dict = {}
      if pathname is None:
        return no_update
      elif pathname == '/':
        result_dict['page_content'] = self.layout_generator.base_layout()
      elif pathname == '/static':
        result_dict['page_content'] = self.layout_generator.static_layout()
      elif pathname == '/embed':
        result_dict['page_content'] = self.layout_generator.embed_layout()
      return mapper.dict_to_output(result_dict)