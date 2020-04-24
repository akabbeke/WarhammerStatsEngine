import os
is_prod = os.environ.get('IS_HEROKU', None) == 'True'
GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', None)
SUBPLOT_COUNT = 2
if is_prod:
  TAB_COUNT = 6
  WEAPON_COUNT = 4
else:
  TAB_COUNT = 2
  WEAPON_COUNT = 2

TAB_COLOURS = [
  '#1f77b4',
  '#ff7f0e',
  '#2ca02c',
  '#d62728',
  '#9467bd',
  '#8c564b',
  '#e377c2',
  '#7f7f7f',
  '#bcbd22',
  '#17becf',
]

DEFUALT_GRAPH_PLOTS = [{}] * TAB_COUNT * SUBPLOT_COUNT