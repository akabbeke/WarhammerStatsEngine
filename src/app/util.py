import re
from ..stats.attack import AttackSequence
from ..stats.pmf import PMF
from ..stats.weapons import Weapon
from ..stats.units import Unit
from ..stats.modifiers import ModifierCollection, ReRollOnes, ReRollFailed, ReRollAll, ReRollLessThanExpectedValue, \
  Melta, AddNToThreshold, AddNToVolume, SetThresholdToN, IgnoreAP, IgnoreInvuln, ModExtraHit, ExtraHit, ModExtraShot, \
  ExtraShot, HalfDamage, AddNToSave, AddNToInvuln, GenerateMortalWound, ModGenerateMortalWound, MinimumValue, Haywire


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

    if 're_roll_dice' in mod:
      mods.append(ReRollAll())
    elif 're_roll_failed' in mod:
      mods.append(ReRollFailed())
    elif 're_roll_1s' in mod:
      mods.append(ReRollOnes())
    elif 'mod_extra_hit_6_1' in mod:
      mods.append(ModExtraHit(6,1))
    elif 'mod_extra_hit_5_1' in mod:
      mods.append(ModExtraHit(5,1))
    elif 'extra_hit_6_1' in mod:
      mods.append(ExtraHit(6,1))
    elif 'extra_hit_5_1' in mod:
      mods.append(ExtraHit(5,1))
    elif 'mod_extra_shot_6_1' in mod:
      mods.append(ModExtraShot(6,1))
    elif 'mod_extra_shot_5_1' in mod:
      mods.append(ModExtraShot(5,1))
    elif 'extra_shot_6_1' in mod:
      mods.append(ExtraShot(6,1))
    elif 'extra_shot_5_1' in mod:
      mods.append(ExtraShot(5,1))
    elif 'mod_mortal_wound_6_1' in mod:
      mods.append(ModGenerateMortalWound(6, 1))
    elif 'mod_mortal_wound_5_1' in mod:
      mods.append(ModGenerateMortalWound(5, 1))
    elif 'mortal_wound_6_1' in mod:
      mods.append(GenerateMortalWound(6, 1))
    elif 'mortal_wound_5_1' in mod:
      mods.append(GenerateMortalWound(5, 1))

  return mods


def wound_modifiers(wound_mods):
  mods = []
  for mod in wound_mods:
    add_match = re.match(r'add_(\d+)', mod)
    sub_match = re.match(r'sub_(\d+)', mod)
    if add_match:
      value = add_match.groups()[0]
      mods.append(AddNToThreshold(int(value)))
    if sub_match:
      value = -1 * int(sub_match.groups()[0])
      mods.append(AddNToThreshold(value))

    if 're_roll_dice' in mod:
      mods.append(ReRollAll())
    elif 're_roll_failed' in mod:
      mods.append(ReRollFailed())
    elif 're_roll_1s' in mod:
      mods.append(ReRollOnes())
    elif 'mod_mortal_wound_6_1' in mod:
      mods.append(ModGenerateMortalWound(6, 1))
    elif 'mod_mortal_wound_5_1' in mod:
      mods.append(ModGenerateMortalWound(5, 1))
    elif 'mortal_wound_6_1' in mod:
      mods.append(GenerateMortalWound(6, 1))
    elif 'mortal_wound_5_1' in mod:
      mods.append(GenerateMortalWound(5, 1))
    elif 'haywire' in mod:
      mods.append(Haywire(5, 1))
  return mods


def save_modifiers(wound_mods):
  mods = []
  for mod in wound_mods:
    add_match = re.match(r'add_(\d+)', mod)
    sub_match = re.match(r'sub_(\d+)', mod)
    add_inv_match = re.match(r'add_inv_(\d+)', mod)
    sub_inv_match = re.match(r'sub_inv_(\d+)', mod)
    if add_match:
      value = add_match.groups()[0]
      mods.append(AddNToSave(int(value)))
    if sub_match:
      value = -1 * int(sub_match.groups()[0])
      mods.append(AddNToSave(value))
    if add_inv_match:
      value = add_inv_match.groups()[0]
      mods.append(AddNToInvuln(int(value)))
    if sub_inv_match:
      value = -1 * int(sub_inv_match.groups()[0])
      mods.append(AddNToInvuln(value))

    if 're_roll_dice' in mod:
      mods.append(ReRollAll())
    elif 're_roll_failed' in mod:
      mods.append(ReRollFailed())
    elif 're_roll_1s' in mod:
      mods.append(ReRollOnes())
    elif 'ignore_ap_1' in mod:
      mods.append(IgnoreAP(1))
    elif 'ignore_ap_2' in mod:
      mods.append(IgnoreAP(2))
    elif 'ignore_invuln' in mod:
      mods.append(IgnoreInvuln())
  return mods


def damage_modifiers(damage_mods):
  mods = []
  for mod in damage_mods:
    add_match = re.match(r'add_(\d+)', mod)
    sub_match = re.match(r'sub_(\d+)', mod)
    if add_match:
      value = add_match.groups()[0]
      mods.append(AddNToVolume(int(value)))
    if sub_match:
      value = -1 * int(sub_match.groups()[0])
      mods.append(AddNToVolume(value))

    if 're_roll_dice' in mod:
      mods.append(ReRollAll())
    elif 're_roll_1s' in mod:
      mods.append(ReRollOnes())
    elif 'melta' in mod:
      mods.append(Melta())
    elif 'half_damage' in mod:
      mods.append(HalfDamage())
    elif 'minimum_3' in mod:
      mods.append(MinimumValue(3))
  return mods


def compute(enable = None, ws=None, toughness=None, strength=None, ap=None, save=None, invuln=None, fnp=None,
            wounds=None, shots=None, damage=None, shot_mods=None, hit_mods=None, wound_mods=None, save_mods=None,
            damage_mods=None):

  if not enable:
    return []

  modifiers = ModifierCollection()
  modifiers.add_mods('shots', shot_modifiers(shot_mods or []))
  modifiers.add_mods('hit', hit_modifiers(hit_mods or []))
  modifiers.add_mods('wound', wound_modifiers(wound_mods or []))
  modifiers.add_mods('pen', save_modifiers(save_mods or []))
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
  attack_sequence = AttackSequence(weapon, target, target, modifiers)

  values = attack_sequence.run().cumulative().trim_tail().values
  return values

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