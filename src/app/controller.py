import dash
import dash_daq as daq
import re
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from .layout import generate_modify_shot_options, generate_modify_hit_options, generate_modify_wound_options, \
  generate_modify_save_options, generate_modify_damage_options, gen_tab_inputs, graph_inputs, graph_figure_template

from .util import compute

from ..constants import TAB_COUNT


def parse_args(args):
  mapped_args = []
  for i in range(0, TAB_COUNT):
    tab_dict = {}
    tab_inputs = gen_tab_inputs(i)
    trim_length = -1 * len('-{}'.format(i))
    for j, input_name in enumerate(tab_inputs):
      tab_dict[input_name[:trim_length]] = args[(len(tab_inputs)*i) + j]
    mapped_args.append(tab_dict)
  return mapped_args

def update_graph(*args):
  graph_args = parse_args(args[:-1])
  graph_data = args[-1]['data']

  if graph_data == [{}] * TAB_COUNT:
    tab_numbers = list(range(TAB_COUNT))
  else:
    tab_numbers = determine_which_tabs_changed(dash.callback_context)

  for tab_number in tab_numbers:
    values = compute(**graph_args[tab_number])
    graph_data[tab_number] = {
      'x': [i for i, x in enumerate(values)],
      'y': [100*x for i, x in enumerate(values)],
      'name': 'P{}'.format(tab_number + 1),
    }

  max_len = max(max([len(x.get('x', [])) for x in graph_data]), 24)

  return graph_figure_template(graph_data, max_len)

def determine_which_tabs_changed(ctx):
  if not ctx:
    return list(range(TAB_COUNT))
  match = re.match(r'.*_(\d+).value', ctx.triggered[0]['prop_id'])
  if not match:
    return list(range(TAB_COUNT))
  else:
    return [int(match.groups()[0]) - 1]

def setup_option_callbacks(app, tab_count):
  for i in range(1, tab_count+1):
    @app.callback(
        dash.dependencies.Output('shot_mods_{}'.format(i), 'options'),
        [dash.dependencies.Input('shot_mods_{}'.format(i), 'value')],
    )
    def update_shot_options(value):
        return generate_modify_shot_options(value or [])

    @app.callback(
        dash.dependencies.Output('hit_mods_{}'.format(i), 'options'),
        [dash.dependencies.Input('hit_mods_{}'.format(i), 'value')],
    )
    def update_hit_options(value):
        return generate_modify_hit_options(value or [])

    @app.callback(
        dash.dependencies.Output('wound_mods_{}'.format(i), 'options'),
        [dash.dependencies.Input('wound_mods_{}'.format(i), 'value')],
    )
    def update_wound_options(value):
        return generate_modify_wound_options(value or [])

    @app.callback(
        dash.dependencies.Output('save_mods_{}'.format(i), 'options'),
        [dash.dependencies.Input('save_mods_{}'.format(i), 'value')],
    )
    def update_save_options(value):
        return generate_modify_save_options(value or [])

    @app.callback(
        dash.dependencies.Output('damage_mods_{}'.format(i), 'options'),
        [dash.dependencies.Input('damage_mods_{}'.format(i), 'value')],
    )
    def update_damage_options(value):
        return generate_modify_damage_options(value or [])

def setup_graph_callback(app, tab_count):
  @app.callback(
    Output('damage-graph', 'figure'),
    [Input(x, 'value') for x in graph_inputs(tab_count)],
    [State('damage-graph', 'figure')]
  )
  def graph_callback(*args):
    return update_graph(*args)

def setup_callbacks(app, tab_count):
  setup_option_callbacks(app, tab_count)
  setup_graph_callback(app, tab_count)

