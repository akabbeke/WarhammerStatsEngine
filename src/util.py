import re
from .stats import AttackSequence
from .pmf import PMF
from .weapons import Weapon
from .units import Unit
from .modifiers import Modifiers

def apply_shot_modifiers(modifiers, shot_modifier):
  if 're_roll_dice' in shot_modifier:
    modifiers._shot_modifier = 're_roll_dice'
    return modifiers
  elif 're_roll_1s' in shot_modifier:
    modifiers._shot_modifier = 're_roll_1s'
    return modifiers
  elif 're_roll_one_dice' in shot_modifier:
    modifiers._shot_modifier = 're_roll_one_dice'
    return modifiers
  else:
    return modifiers

def apply_hit_modifiers(modifiers, shot_modifier):
  mod_value = 0
  for mod in shot_modifier:
    if mod == 'add_1':
      mod_value -= 1
    if mod == 'add_2':
      mod_value -= 2
    if mod == 'add_3':
      mod_value -= 3
    if mod == 'sub_1':
      mod_value += 1
    if mod == 'sub_2':
      mod_value += 2
    if mod == 'sub_3':
      mod_value += 3
  modifiers._hit_modifier = mod_value

  if 're_roll_dice' in shot_modifier:
    modifiers._hit_re_roll = 're_roll_dice'
    return modifiers
  elif 're_roll_failed' in shot_modifier:
    modifiers._hit_re_roll = 're_roll_failed'
    return modifiers
  elif 're_roll_1s' in shot_modifier:
    modifiers._hit_re_roll = 're_roll_1s'
    return modifiers
  else:
    return modifiers

def apply_wound_modifiers(modifiers, wound_modifier):
  mod_value = 0
  for mod in wound_modifier:
    if mod == 'add_1':
      mod_value -= 1
    if mod == 'add_2':
      mod_value -= 2
    if mod == 'add_3':
      mod_value -= 3
    if mod == 'sub_1':
      mod_value += 1
    if mod == 'sub_2':
      mod_value += 2
    if mod == 'sub_3':
      mod_value += 3
  modifiers._wound_modifier = mod_value

  if 're_roll_dice' in wound_modifier:
    modifiers._wound_re_roll = 're_roll_dice'
    return modifiers
  elif 're_roll_failed' in wound_modifier:
    modifiers._wound_re_roll = 're_roll_failed'
    return modifiers
  elif 're_roll_1s' in wound_modifier:
    modifiers._wound_re_roll = 're_roll_1s'
    return modifiers
  else:
    return modifiers

def apply_damage_modifiers(modifiers, damage_modifier):
  mod_value = 0
  for mod in damage_modifier:
    if mod == 'add_1':
      mod_value += 1
    if mod == 'add_2':
      mod_value += 2
    if mod == 'add_3':
      mod_value += 3
    if mod == 'sub_1':
      mod_value -= 1
    if mod == 'sub_2':
      mod_value -= 2
    if mod == 'sub_3':
      mod_value -= 3
  modifiers._damage_modifier = mod_value

  if 're_roll_dice' in damage_modifier:
    modifiers._damage_re_roll= 're_roll_dice'
    return modifiers
  elif 're_roll_1s' in damage_modifier:
    modifiers._damage_re_roll = 're_roll_1s'
    return modifiers
  elif 'roll_two_choose_highest' in damage_modifier:
    modifiers._damage_re_roll = 'roll_two_choose_highest'
    return modifiers
  elif 're_roll_one_dice' in damage_modifier:
    modifiers._damage_re_roll = 're_roll_one_dice'
    return modifiers
  else:
    return modifiers

def compute(toughness, save, invuln, fnp, wounds, ws, shots, strength, ap, damage,
            shot_modifier, hit_modifier, wound_modifier, damage_modifier, cumulative=True):

  modifiers = Modifiers()
  modifiers = apply_shot_modifiers(modifiers, shot_modifier or [])
  modifiers = apply_hit_modifiers(modifiers, hit_modifier or [])
  modifiers = apply_wound_modifiers(modifiers, wound_modifier or [])
  modifiers = apply_damage_modifiers(modifiers, damage_modifier or [])

  target = Unit(
    ws=int(ws or 1),
    bs=int(ws or 1),
    toughness=int(toughness or 1),
    save=int(save or 1),
    invul=int(invuln or 1),
    fnp=int(fnp or 7),
    wounds=int(wounds or 1),
  )
  weapon = Weapon(
    shots=parse_rsn(shots or 1),
    strength=int(strength or 1),
    ap=int(ap or 0),
    damage=parse_rsn(damage or 1),
  )
  basic = AttackSequence(
    weapon,
    target,
    target,
    modifiers,
  )

  return basic.run().cumulative().trim_tail().values

def parse_rsn(value):
  try:
    return [PMF.static(int(value or 1))]
  except ValueError:
    number, faces = re.match('(?P<number>\d+)?d(?P<faces>\d+)', value).groups()
    return [PMF.dn(int(faces))] * (int(number) if number else 1)