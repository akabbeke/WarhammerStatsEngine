import os
is_prod = os.environ.get('IS_HEROKU', None)
GA_TRACKING_ID = os.environ.get('GA_TRACKING_ID', None)
if is_prod:
  TAB_COUNT = 6
  WEAPON_COUNT = 4
else:
  TAB_COUNT = 2
  WEAPON_COUNT = 2