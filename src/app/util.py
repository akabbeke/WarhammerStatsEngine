import re
from ..stats.attack import AttackSequence
from ..stats.pmf import PMF
from ..stats.weapons import Weapon
from ..stats.units import Unit
from ..stats.modifiers import ModifierCollection, ReRollOnes, ReRollFailed, ReRollAll, ReRollLessThanExpectedValue, \
  Melta, AddNToThreshold, AddNToVolume, SetThresholdToN, IgnoreAP, IgnoreInvuln, ModExtraHit, ExtraHit, ModExtraShot, \
  ExtraShot, HalfDamage, AddNToSave, AddNToInvuln, GenerateMortalWound, ModGenerateMortalWound, MinimumValue, Haywire


def parse_shot_mods(shot_mods):
  if not shot_mods:
    return [], []
  mods = []
  errors = []

  for mod in [x.strip() for x in shot_mods.lower().split(',')]:
    mod_mods = []
    mod_mods += parse_addons(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_volume_rerolls(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_special(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_add(mod)

    if not mod_mods:
      errors.append(f'"{mod}" is not a valid shot modifier')
    mods += mod_mods
  return mods, errors

def parse_hit_mods(shot_mods):
  if not shot_mods:
    return [], []
  mods = []
  errors = []

  for mod in [x.strip() for x in shot_mods.lower().split(',')]:
    mod_mods = []
    mod_mods += parse_addons(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_rerolls(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_special(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_add(mod)
    if mod_mods:
      mods += mod_mods
      continue


    if not mod_mods:
      errors.append(f'"{mod}" is not a valid hit modifier')
    mods += mod_mods
  return mods, errors

def parse_wound_mods(shot_mods):
  if not shot_mods:
    return [], []
  mods = []
  errors = []

  for mod in [x.strip() for x in shot_mods.lower().split(',')]:
    mod_mods = []
    mod_mods += parse_addons(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_rerolls(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_special(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_add(mod)
    if mod_mods:
      mods += mod_mods
      continue

    if not mod_mods:
      errors.append(f'"{mod}" is not a valid wound modifier')
    mods += mod_mods
  return mods, errors

def parse_save_mods(shot_mods):
  if not shot_mods:
    return [], []
  mods = []
  errors = []

  for mod in [x.strip() for x in shot_mods.lower().split(',')]:
    mod_mods = []
    mod_mods += parse_rerolls(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_ignore(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_save_add(mod)
    if mod_mods:
      mods += mod_mods
      continue

    if not mod_mods:
      errors.append(f'"{mod}" is not a valid save modifier')
    mods += mod_mods
  return mods, errors

def parse_damage_mods(shot_mods):
  if not shot_mods:
    return [], []
  mods = []
  errors = []

  for mod in [x.strip() for x in shot_mods.lower().split(',')]:
    mod_mods = []
    mod_mods += parse_volume_rerolls(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_ignore(mod)
    if mod_mods:
      mods += mod_mods
      continue
    mod_mods += parse_add(mod)
    if mod_mods:
      mods += mod_mods
      continue

    if not mod_mods:
      errors.append(f'"{mod}" is not a valid damage modifier')
    mods += mod_mods
  return mods, errors

def parse_addons(mod):
  mods = []
  match = re.match(r'\+?(?P<added_value>[0-9]+) (?P<added_kind>.*) on (a )?(?P<trigger>[0-9]+)(?P<threshold>\+)?', mod)
  if not match:
    return mods


  added_value = match.groupdict().get('added_value')
  added_kind = match.groupdict().get('added_kind')
  trigger = match.groupdict().get('trigger')
  threshold = match.groupdict().get('threshold')

  int(added_value)

  if added_kind in ['mw', 'mortal wound', 'mortal', 'mws', 'mortal wounds', 'mw\'s', 'mortal wound\'s']:
    if threshold:
      mods.append(ModGenerateMortalWound(int(trigger), int(added_value)))
    else:
      mods.append(GenerateMortalWound(int(trigger), int(added_value)))
  elif added_kind in ['hit', 'hits']:
    if threshold:
      mods.append(ModExtraHit(int(trigger), int(added_value)))
    else:
      mods.append(ExtraHit(int(trigger), int(added_value)))
  elif added_kind in ['shot', 'shots']:
    if threshold:
      mods.append(ModExtraShot(int(trigger), int(added_value)))
    else:
      mods.append(ExtraShot(int(trigger), int(added_value)))
  return mods

def parse_rerolls(mod):
  mods = []
  match = re.match(r'(re(-)?roll) (?P<reroll_kind>.+)', mod)
  if not match:
    return mods

  reroll_kind = match.groupdict().get('reroll_kind')
  if reroll_kind in ['one', 'ones', '1', '1\'s']:
    mods.append(ReRollOnes())
  elif reroll_kind in ['all', 'all dice', 'all die', 'all rolls', 'all roll']:
    mods.append(ReRollAll())
  elif reroll_kind in ['all failed', 'all failed dice', 'all failed rolls', 'all failed die']:
    mods.append(ReRollFailed())
  return mods

def parse_volume_rerolls(mod):
  mods = []
  match = re.match(r'(re(-)?roll) (?P<reroll_kind>.+)', mod)
  if not match:
    return mods

  reroll_kind = match.groupdict().get('reroll_kind')
  if reroll_kind in ['one', 'ones', '1', '1\'s']:
    mods.append(ReRollOnes())
  elif reroll_kind in ['all', 'all dice', 'all die', 'all rolls', 'all roll']:
    mods.append(ReRollLessThanExpectedValue())
  return mods

def parse_special(mod):
  mods = []
  if 'haywire' in mod:
    mods.append(Haywire(5, 1))
  elif mod in ['roll 2 choose highest', 'roll two choose highest', 'melta']:
    mods.append(Melta())
  elif mod in ['half damage']:
    mods.append(HalfDamage())
  elif mod in ['minimum 3 damage', 'treat rolls of 1 and 2 as 3']:
    mods.append(MinimumValue(3))
  return mods

def parse_add(mod):
  mods = []
  match = re.match(r'(?P<modify_type>add|sub|subtract)?( )?(?P<modifier>\+|-)?(?P<raw_value>\d+)', mod)
  if not match:
    return mods
  modify_type = match.groupdict().get('modify_type')
  modifier = match.groupdict().get('modifier')
  raw_value = match.groupdict().get('raw_value')

  value = int(raw_value)
  if modify_type in ['sub', 'subtract'] or modifier == '-':
    value = -1*int(value)

  mods.append(AddNToThreshold(value))
  return mods

def parse_ignore(mod):
  mods = []
  match = re.match(r'ignore (?P<modifier>[^-\s]+) (\+|-)?(?P<value>\d+)', mod)
  if not match:
    return mods
  modifier = match.groupdict().get('modifier')
  value = match.groupdict().get('value')

  value = int(value)
  if modifier in ['ap']:
    mods.append(IgnoreAP(value))
  elif modifier in ['inv', 'invuln', 'invulnerable']:
    mods.append(IgnoreInvuln())
  return mods

def parse_save_add(mod):
  mods = []
  match = re.match(
    r'(?P<modify_type>add|sub|subtract)?( )?(?P<modifier>\+|-)?(?P<raw_value>\d+)(( to)? (?P<type>(?!to).+))?',
    mod
  )
  if not match:
    return mods
  modify_type = match.groupdict().get('modify_type')
  modifier = match.groupdict().get('modifier')
  raw_value = match.groupdict().get('raw_value')
  save_type = match.groupdict().get('type')

  value = int(raw_value)
  if modify_type in ['sub', 'subtract'] or modifier == '-':
    value = -1*int(value)
  if save_type in [None, 'save']:
    mods.append(AddNToSave(value))
  elif save_type in ['inv', 'invuln', 'invulnerable']:
    mods.append(AddNToInvuln(value))
  return mods


def compute(enabled = None, tab_name=None, ws=None, toughness=None, strength=None, ap=None, save=None, invuln=None, fnp=None,
            wounds=None, shots=None, damage=None, shot_mods=None, hit_mods=None, wound_mods=None, save_mods=None,
            damage_mods=None, existing_data=None, re_render=True, tab_index=None):

  if (not re_render and not existing_data) or not enabled:
    return {
      'graph_data': {},
      'mean': 0,
      'std': 0,
      'errors': []
    }
  elif not re_render:
    existing_data[tab_index]['name'] = tab_name
    return {
      'graph_data': existing_data[tab_index],
      'errors': []
    }

  shot_mod_list, shot_mod_error = parse_shot_mods(shot_mods)
  hit_mod_list, hit_mod_error = parse_hit_mods(hit_mods)
  wound_mod_list, wound_mod_error = parse_wound_mods(wound_mods)
  save_mod_list, save_mod_error = parse_save_mods(save_mods)
  damage_mod_list, damage_mod_error = parse_damage_mods(damage_mods)

  modifiers = ModifierCollection()
  modifiers.add_mods('shots', shot_mod_list)
  modifiers.add_mods('hit', hit_mod_list)
  modifiers.add_mods('wound', wound_mod_list)
  modifiers.add_mods('pen', save_mod_list)
  modifiers.add_mods('damage', damage_mod_list)

  target = Unit(
    ws=int(ws or 1),
    bs=int(ws or 1),
    toughness=int(toughness or 1),
    save=int(save or 7),
    invul=int(invuln or 7),
    fnp=int(fnp or 7),
    wounds=int(wounds or 1),
  )
  weapon = Weapon(
    shots=parse_rsn(shots or 1),
    strength=int(strength or 1),
    ap=int(ap or 0),
    damage=parse_rsn(damage or 1),
  )
  attack_sequence = AttackSequence(weapon, target, target, modifiers)
  attack_pmf = attack_sequence.run()
  values = attack_pmf.cumulative().trim_tail().values

  graph_data = {
    'x': [i for i, x in enumerate(values)],
    'y': [100*x for i, x in enumerate(values)],
    'name': tab_name,
    "colorscale": [[0, "rgba(255, 255, 255,0)"], [1, "#75baf2"]],
  }
  output = {
    'graph_data': graph_data,
    'mean': attack_pmf.mean(),
    'std': attack_pmf.std(),
    'errors': shot_mod_error + hit_mod_error + wound_mod_error + save_mod_error + damage_mod_error,
  }
  if shot_mods:
    output['shot_mod_error'] = shot_mod_error
  if hit_mods:
    output['hit_mod_error'] = hit_mod_error
  if wound_mods:
    output['wound_mod_error'] = wound_mod_error
  if save_mods:
    output['save_mod_error'] = save_mod_error
  if damage_mods:
    output['damage_mod_error'] = damage_mod_error

  return output

def parse_rsn(value):
  try:
    return [PMF.static(int(value or 1))]
  except ValueError:
    match = re.match(r'(?P<number>\d+)?d(?P<faces>\d+)', value.lower())
    if match:
      number, faces = re.match(r'(?P<number>\d+)?d(?P<faces>\d+)', value.lower()).groups()
      return [PMF.dn(int(faces))] * (int(number) if number else 1)
    else:
      return []