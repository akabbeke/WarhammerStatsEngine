import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

from .graph_layout import GraphLayout
from .input_layout import InputLayout


class Layout(object):
  def __init__(self, tab_count=0, weapon_count=0):
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def layout(self):
    return html.Div([
      dcc.Location(id='url'),
      html.Div(id='page_content')
    ])

  def base_layout(self):
    return html.Div(
      [
        self.navbar(),
        dbc.Select(),
        self.base_title(),
        dbc.Row(
          dbc.Col(
            GraphLayout(self.tab_count).layout(),
            className='portlet-container portlet-dropzone',
          ),
          style={'align-items': 'center'},
          className='flex-fill fill d-flex justify-content-start',
        ),
        dbc.Row(
          [
            dbc.Col(
              InputLayout(self.tab_count, self.weapon_count).layout(),
            ),
          ]
        ),
      ],
    )

  def base_title(self):
    content = dbc.InputGroup(
      [
        dbc.InputGroupAddon("Title", addon_type="prepend"),
        dbc.Input(
          type="text",
          id='title',
          value='',
          debounce=True,
          minLength=2,
          persistence=True,
          persistence_type='session',
          maxLength=140,
        ),
      ],
    )
    return dbc.CardBody(dbc.Row([dbc.Col(content)], className="mb-2 ",))

  def static_layout(self):
    return html.Div(
      [
        self.static_navbar(),
        html.Div(id='static_graph_debug', style={'display': 'none'}),
        dcc.RadioItems(
          id='page-2-radios',
          options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
          value='Orange',
          style={'display': 'none'}
        ),
        dbc.Row(
          dbc.Col(
            [
              GraphLayout(self.tab_count).static_layout(),
              *self._data_area(),
            ],
            className='portlet-container portlet-dropzone',
          ),
          style={'align-items': 'center'},
          className='flex-fill fill d-flex justify-content-start',
        ),

      ],
    )

  def embed_layout(self):
    return html.Div(
      [
        GraphLayout(self.tab_count).embed_layout(),
        dcc.RadioItems(
          id='page-2-radios',
          options=[{'label': i, 'value': i} for i in ['Orange', 'Blue', 'Red']],
          value='Orange',
          style={'display': 'none'}
        ),
      ],
      className='container-fluid d-flex flex-column',
    )

  def _data_area(self):
    return [dbc.Row([], id=f'statsrow_{i}', className='mb-2')for i in range(self.tab_count)]



  def navbar(self):
    return dbc.NavbarSimple(
      children=[
        dbc.NavItem(
          dbc.NavLink(
            'GitHub',
            id='github_link',
            href="https://github.com/akabbeke/WarhammerStatsEngine",
            external_link=True,
          )
        ),
        dbc.NavItem(
          dbc.NavLink(
            "Permalink this graph",
            id='permalink',
            href='/',
            external_link=True,
          )
        ),
      ],
      brand="Warhammer Stats Engine",
      brand_href="/",
      brand_external_link=True,
      color="primary",
      dark=True,
    )

  def static_navbar(self):
    return dbc.NavbarSimple(
      children=[
        dbc.NavItem(
          dbc.NavLink(
            "Create your own graph",
            id='permalink',
            href="/",
            external_link=True,
          )
        ),
      ],
      brand="Warhammer Stats Engine",
      brand_href="/",
      brand_external_link=True,
      color="primary",
      dark=True,
    )
