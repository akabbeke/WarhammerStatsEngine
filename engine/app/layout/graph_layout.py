
import dash_core_components as dcc


app_color = {"graph_bg": "#082255", "graph_line": "#a3a7b0"}


class GraphLayout(object):
  def __init__(self, tab_count=0):
    self.tab_count = tab_count

  def layout(self):
    content = dcc.Graph(
      id='damage_graph',
      style={'height':'50vh'},
      figure=self.figure_template(top=10),
      config={
        'scrollZoom': False,
        'toImageButtonOptions': {
          'format': 'jpeg',
          'filename': 'warhammer_plot',
          'height': 1080,
          'width': 1920,
          'scale': 1
        },
        # 'displayModeBar': False,
      },

    )
    return content

  def static_layout(self):
    content = dcc.Graph(
      id='static_damage_graph',
      style={'height':'85vh'},
      figure=self.figure_template(),
      config={
        'scrollZoom': False,
        'toImageButtonOptions': {
          'format': 'jpeg',
          'filename': 'warhammer_plot',
          'height': 1080,
          'width': 1920,
          'scale': 1
        },
        # 'displayModeBar': False,
      },

    )
    return content

  def embed_layout(self):
    content = dcc.Graph(
      id='static_damage_graph',
      style={'height':'95vh'},
      figure=self.figure_template(),
      config={
        'scrollZoom': False,
        'toImageButtonOptions': {
          'format': 'jpeg',
          'filename': 'warhammer_plot',
          'height': 1080,
          'width': 1920,
          'scale': 1
        },
      },
    )
    return content

  def figure_template(self, data=None, max_len=10, title=None, static=False, top=50):
    return {
      'data': data or [{}] * self.tab_count,
      'layout': {
        'title': title,
        'showlegend': True,
        'legend': dict(orientation='h',yanchor='top',xanchor='center',y=1, x=0.5),
        # 'template': 'plotly_dark',
        'xaxis': {
            'title': 'Minimum Wounds Dealt to Target',
            'type': 'linear',
            'range': [0, max_len],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 1,
            "gridcolor": app_color["graph_line"],
            "color": app_color["graph_line"],
            'fixedrange': True,
        },
        'yaxis': {
            'title': 'Probability of Minimum Wounds Dealt',
            'type': 'linear',
            'range': [0, 100],
            'tickmode': 'linear',
            'tick0': 0,
            'dtick': 10,
            "gridcolor": app_color["graph_line"],
            "color": app_color["graph_line"],
            'fixedrange': True,
        },
        'margin':{
          'l': 70,
          'r': 70,
          'b': 50,
          't': top,
          'pad': 4,
        },
        'autosize': True,
      },
    }

