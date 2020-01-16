import re
from ..stats.attack import AttackSequence
from ..stats.pmf import PMF
from ..stats.weapons import Weapon
from ..stats.units import Unit
from ..stats.modifiers import ModifierCollection, ReRollOnes, ReRollFailed, ReRollAll, ReRollLessThanExpectedValue, \
  Melta, AddNToThreshold, AddNToVolume, SetThresholdToN, IgnoreAP, IgnoreInvuln, ModExtraHit, ExtraHit, ModExtraShot, \
  ExtraShot, HalfDamage, AddNToSave, AddNToInvuln, GenerateMortalWound, ModGenerateMortalWound, MinimumValue, Haywire, \
  ReRollOneDice, ModReRollOneDice, ReRollOneDiceVolume


def parse_mods(raw_mods):
  if not raw_mods:
    return []
  mods = []
  for mod in raw_mods:
    match = re.match(r'(?P<mod_type>[a-zA-Z]+)_?(?P<mod_data>.+)?', mod)
    if not match:
      continue
    mod_type = match.groupdict().get('mod_type')
    mod_data = match.groupdict().get('mod_data')

    if mod_type == 'reroll':
      if mod_data == 'allvol':
        mods.append(ReRollLessThanExpectedValue())
      elif mod_data == 'one_dicevol':
        mods.append(ReRollOneDiceVolume())
      elif mod_data == 'ones':
        mods.append(ReRollOnes())
      elif mod_data == 'melta':
        mods.append(Melta())
      elif mod_data == 'all':
        mods.append(ReRollAll())
      elif mod_data == 'failed':
        mods.append(ReRollFailed())
      elif mod_data == 'one_dice':
        mods.append(ModReRollOneDice())
    elif mod_type == 'add':
      mods.append(AddNToThreshold(int(mod_data)))
    elif mod_type == 'sub':
      mods.append(AddNToThreshold(-1*int(mod_data)))
    elif mod_type == 'addon':
      match = re.match(r'(?P<value>\d+)_(?P<addon>[a-zA-Z]+)_(?P<thresh>\d+)(?P<modable>_mod)?', mod_data.lower())
      if not match:
        continue
      value = match.groupdict().get('value')
      addon = match.groupdict().get('addon')
      thresh = match.groupdict().get('thresh')
      modable = match.groupdict().get('modable')
      if modable:
        if addon == 'mw':
          mods.append(ModGenerateMortalWound(int(thresh), int(value)))
        elif addon == 'hit':
          mods.append(ModExtraHit(int(thresh), int(value)))
        elif addon == 'shot':
          mods.append(ModExtraShot(int(thresh), int(value)))
      else:
        if addon == 'mw':
          mods.append(GenerateMortalWound(int(thresh), int(value)))
        elif addon == 'hit':
          mods.append(ExtraHit(int(thresh), int(value)))
        elif addon == 'shot':
          mods.append(ExtraShot(int(thresh), int(value)))
    elif mod_type == 'haywire':
      mods.append(Haywire(5, 1))
    elif mod_type == 'ignoreap':
      mods.append(IgnoreAP(int(mod_data)))
    elif mod_type == 'ignoreinv':
      mods.append(IgnoreInvuln())
    elif mod_type == 'saveadd':
      mods.append(AddNToSave(int(mod_data)))
    elif mod_type == 'savesub':
      mods.append(AddNToSave(-1*int(mod_data)))
    elif mod_type == 'invadd':
      mods.append(AddNToInvuln(int(mod_data)))
    elif mod_type == 'invsub':
      mods.append(AddNToInvuln(-1*int(mod_data)))
    elif mod_type == 'halfdam':
      mods.append(HalfDamage())
    elif mod_type == 'minval':
      mods.append(MinimumValue(int(mod_data)))
  return mods


def compute(enabled = None, tab_name=None, ws=None, toughness=None, strength=None, ap=None, save=None, invuln=None, fnp=None,
            wounds=None, shots=None, damage=None, shot_mods=None, hit_mods=None, wound_mods=None, save_mods=None,
            damage_mods=None, existing_data=None, re_render=True, tab_index=None, title=None):

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

  modifiers = ModifierCollection()
  modifiers.add_mods('shots', parse_mods(shot_mods))
  modifiers.add_mods('hit', parse_mods(hit_mods))
  modifiers.add_mods('wound', parse_mods(wound_mods))
  modifiers.add_mods('pen', parse_mods(save_mods))
  modifiers.add_mods('damage', parse_mods(damage_mods))

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
  }
  output = {
    'graph_data': graph_data,
    'mean': attack_pmf.mean(),
    'std': attack_pmf.std(),
  }

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