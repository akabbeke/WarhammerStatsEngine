import dash
import dash_daq as daq
import re
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from .layout import GraphLayout, InputGenerator, MultiOptionGenerator

from .util import compute

from ..constants import TAB_COUNT

def parse_args(args):
  mapped_args = []
  for i in range(0, TAB_COUNT):
    tab_dict = {}
    tab_inputs = InputGenerator().gen_tab_inputs(i)
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
      'name': 'P{}'.format(tab_number),
    }

  max_len = max(max([len(x.get('x', [])) for x in graph_data]), 24)

  return GraphLayout().figure_template(graph_data, max_len)

def determine_which_tabs_changed(ctx):
  print(ctx.triggered)
  if not ctx:
    return list(range(TAB_COUNT))
  match = re.match(r'.*_(\d+).value', ctx.triggered[0]['prop_id'])
  if not match:
    return list(range(TAB_COUNT))
  else:
    return [int(match.groups()[0])]

def setup_option_callbacks(app, tab_count):
  for i in range(tab_count):
    @app.callback(
      [
        dash.dependencies.Output('damage_mods_{}'.format(i), 'disabled'),
        dash.dependencies.Output('save_mods_{}'.format(i), 'disabled'),
        dash.dependencies.Output('wound_mods_{}'.format(i), 'disabled'),
        dash.dependencies.Output('hit_mods_{}'.format(i), 'disabled'),
        dash.dependencies.Output('shot_mods_{}'.format(i), 'disabled'),

        dash.dependencies.Output('ws_{}'.format(i), 'disabled'),
        dash.dependencies.Output('toughness_{}'.format(i), 'disabled'),
        dash.dependencies.Output('strength_{}'.format(i), 'disabled'),
        dash.dependencies.Output('ap_{}'.format(i), 'disabled'),
        dash.dependencies.Output('save_{}'.format(i), 'disabled'),
        dash.dependencies.Output('invuln_{}'.format(i), 'disabled'),
        dash.dependencies.Output('fnp_{}'.format(i), 'disabled'),
        dash.dependencies.Output('wounds_{}'.format(i), 'disabled'),

        dash.dependencies.Output('shots_{}'.format(i), 'disabled'),
        dash.dependencies.Output('damage_{}'.format(i), 'disabled'),
      ],
      [dash.dependencies.Input('enable_{}'.format(i), 'value')],
    )
    def disable_damage_options(enable):
        return [not enable] * 15

    @app.callback(
      dash.dependencies.Output('tab_{}'.format(i), 'label'),
      [dash.dependencies.Input('tab_name_{}'.format(i), 'value')],
    )
    def update_tab_name(value):
        return value if len(value) > 2 else 'Profile'

    @app.callback(
      dash.dependencies.Output('shot_mods_{}'.format(i), 'options'),
      [dash.dependencies.Input('shot_mods_{}'.format(i), 'value')],
    )
    def update_shot_options(value):
        return MultiOptionGenerator().shot_options(value or [])

    @app.callback(
      dash.dependencies.Output('hit_mods_{}'.format(i), 'options'),
      [dash.dependencies.Input('hit_mods_{}'.format(i), 'value')],
    )
    def update_hit_options(value):
        return MultiOptionGenerator().hit_options(value or [])

    @app.callback(
      dash.dependencies.Output('wound_mods_{}'.format(i), 'options'),
      [dash.dependencies.Input('wound_mods_{}'.format(i), 'value')],
    )
    def update_wound_options(value):
        return MultiOptionGenerator().wound_options(value or [])

    @app.callback(
      dash.dependencies.Output('save_mods_{}'.format(i), 'options'),
      [dash.dependencies.Input('save_mods_{}'.format(i), 'value')],
    )
    def update_save_options(value):
        return MultiOptionGenerator().save_options(value or [])

    @app.callback(
      dash.dependencies.Output('damage_mods_{}'.format(i), 'options'),
      [dash.dependencies.Input('damage_mods_{}'.format(i), 'value')],
    )
    def update_damage_options(value):
        return MultiOptionGenerator().damage_options(value or [])

    # @app.callback(
    #   generate_target_lock_output(i),
    #   [dash.dependencies.Input('target-apply-all-{}'.format(i), 'n_clicks')],
    #   generate_target_lock_state(i),
    # )
    # def update_damage_options(value):
    #     return MultiOptionGenerator().damage_options(value or [])

def generate_target_lock_output(tab_index):
  outputs = []
  for i in [x for x in range(TAB_COUNT) if x!=tab_index]:
    outputs = [Output(y, 'value') for y in InputGenerator().target_row_input(i)]
  print(outputs)
  return outputs

def generate_target_lock_state(tab_index):
  return [State(y, 'value') for y in InputGenerator().target_row_input(tab_index)]

def setup_graph_callback(app, tab_count):
  @app.callback(
    Output('damage-graph', 'figure'),
    [Input(x, 'value') for x in InputGenerator().graph_inputs(tab_count)],
    [State('damage-graph', 'figure')]
  )
  def graph_callback(*args):
    return update_graph(*args)

def setup_callbacks(app, tab_count):
  setup_option_callbacks(app, tab_count)
  setup_graph_callback(app, tab_count)
  pass

