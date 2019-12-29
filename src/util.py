import re
from .stats import AttackSequence
from .pmf import PMF
from .weapons import Weapon
from .units import Unit
from .modifiers import ModifierCollection, ReRollOnes, ReRollFailed, ReRollAll, ReRollLessThanExpectedValue, \
  Melta, AddNToThreshold, AddNToVolume, SetThresholdToN, IgnoreAP, RemoveInvuln


def shot_modifiers(shot_mods):
  mods = []
  if 're_roll_dice' in shot_mods:
    mods.append(ReRollLessThanExpectedValue())
  elif 're_roll_1s' in shot_mods:
    mods.append(ReRollOnes())
  return mods


def hit_modifiers(hit_mods):
  mods = []
  for mod in hit_mods:
    add_match = re.match(r'add_(\d+)', mod)
    sub_match = re.match(r'sub_(\d+)', mod)
    if add_match:
      value = int(add_match.groups()[0])
      mods.append(AddNToThreshold(value))
    if sub_match:
      value = -1 * int(sub_match.groups()[0])
      mods.append(AddNToThreshold(value))

  if 're_roll_dice' in hit_mods:
    mods.append(ReRollAll())
  elif 're_roll_failed' in hit_mods:
    mods.append(ReRollFailed())
  elif 're_roll_1s' in hit_mods:
    mods.append(ReRollOnes())

  return mods


def wound_modifiers(wound_mods):
  mods = []
  for mod in wound_mods:
    add_match = re.match(r'add_(\d+)', mod)
    sub_match = re.match(r'sub_(\d+)', mod)
    if add_match:
      value = add_match.groups()[0]
      mods.append(AddNToThreshold(value))
    if sub_match:
      value = -1 * sub_match.groups()[0]
      mods.append(AddNToThreshold(value))

  if 're_roll_dice' in wound_mods:
    mods.append(ReRollAll())
  elif 're_roll_failed' in wound_mods:
    mods.append(ReRollFailed())
  elif 're_roll_1s' in wound_mods:
    mods.append(ReRollOnes())
  return mods


def damage_modifiers(damage_mods):
  mods = []
  for mod in damage_mods:
    add_match = re.match(r'add_(\d+)', mod)
    sub_match = re.match(r'sub_(\d+)', mod)
    if add_match:
      value = add_match.groups()[0]
      mods.append(AddNToThreshold(value))
    if sub_match:
      value = -1 * sub_match.groups()[0]
      mods.append(AddNToThreshold(value))

  if 're_roll_dice' in damage_mods:
    mods.append(ReRollAll())
  elif 're_roll_1s' in damage_mods:
    mods.append(ReRollOnes())
  return mods


def compute(enable = None, ws=None, toughness=None, strength=None, ap=None, save=None, invuln=None, fnp=None,
            wounds=None, shots=None, damage=None, shot_mods=None, hit_mods=None, wound_mods=None, damage_mods=None):

  if not enable:
    return []

  # print(dict(
  #   ws=int(ws or 1),
  #   bs=int(ws or 1),
  #   toughness=int(toughness or 1),
  #   save=8-int(save or 1),
  #   invul=8-int(invuln or 1),
  #   fnp=8-int(fnp or 1),
  #   wounds=int(wounds or 1),
  #   shots=parse_rsn(shots or 1),
  #   strength=int(strength or 1),
  #   ap=int(ap or 0),
  #   damage=parse_rsn(damage or 1),
  #   shot_modifiers=shot_modifiers,
  #   hit_modifiers=hit_modifiers,
  #   wound_modifiers=wound_modifiers,
  #   damage_modifiers=damage_modifiers,
  # ))

  modifiers = ModifierCollection()
  modifiers.add_mods('shots', shot_modifiers(shot_mods or []))
  modifiers.add_mods('hit', hit_modifiers(hit_mods or []))
  modifiers.add_mods('wound', wound_modifiers(wound_mods or []))
  modifiers.add_mods('damage', damage_modifiers(damage_mods or []))

  target = Unit(
    ws=int(ws or 1),
    bs=int(ws or 1),
    toughness=int(toughness or 1),
    save=8-int(save or 1),
    invul=8-int(invuln or 1),
    fnp=8-int(fnp or 1),
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

  values = basic.run().cumulative().trim_tail().values
  return values

def parse_rsn(value):
  try:
    return [PMF.static(int(value or 1))]
  except ValueError:
    match = re.match(r'(?P<number>\d+)?d(?P<faces>\d+)', value)
    if match:
      number, faces = re.match(r'(?P<number>\d+)?d(?P<faces>\d+)', value).groups()
      return [PMF.dn(int(faces))] * (int(number) if number else 1)
    else:
      return []