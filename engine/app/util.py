import re
from ..stats.attack import AttackSequence
from ..stats.pmf import PMF, PMFCollection
from ..stats.weapons import Weapon
from ..stats.units import Unit
from ..stats.modifiers import ModifierCollection, ReRollOnes, ReRollFailed, ReRollAll, ReRollLessThanExpectedValue, \
  Melta, AddNToThreshold, AddNToVolume, SetThresholdToN, IgnoreAP, IgnoreInvuln, ModExtraHit, ExtraHit, ModExtraAttack, \
  ExtraShot, HalfDamage, AddNToSave, AddNToInvuln, GenerateMortalWound, ModGenerateMortalWound, MinimumValue, Haywire, \
  ReRollOneDice, ModReRollOneDice, ReRollOneDiceVolume, AddD6, AddD3, ModExtraWound, ExtraWound, ShieldDrone, NormalDrone, \
  Overheat


class ComputeController(object):
  def parse_mods(self, raw_mods):
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
          elif addon == 'hits':
            mods.append(ModExtraHit(int(thresh), int(value)))
          elif addon == 'shots':
            mods.append(ModExtraAttack(int(thresh), int(value)))
          elif addon == 'wounds':
            mods.append(ModExtraWound(int(thresh), int(value)))
        else:
          if addon == 'mw':
            mods.append(GenerateMortalWound(int(thresh), int(value)))
          elif addon == 'hits':
            mods.append(ExtraHit(int(thresh), int(value)))
          elif addon == 'shots':
            mods.append(ExtraShot(int(thresh), int(value)))
          elif addon == 'wounds':
            mods.append(ExtraWound(int(thresh), int(value)))
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
      elif mod_type == 'fnpadd':
        mods.append(AddNToSave(int(mod_data)))
      elif mod_type == 'fnpsub':
        mods.append(AddNToSave(-1*int(mod_data)))
      elif mod_type == 'invadd':
        mods.append(AddNToInvuln(int(mod_data)))
      elif mod_type == 'invsub':
        mods.append(AddNToInvuln(-1*int(mod_data)))
      elif mod_type == 'halfdam':
        mods.append(HalfDamage())
      elif mod_type == 'minval':
        mods.append(MinimumValue(int(mod_data)))
      elif mod_type == 'addvol':
        if mod_data == 'd6':
          mods.append(AddD6())
        elif mod_data == 'd3':
          mods.append(AddD3())
        else:
          mods.append(AddNToVolume(int(mod_data)))
      elif mod_type == 'subvol':
        mods.append(AddNToVolume(-1*int(mod_data)))
      elif mod_type == 'shielddrone':
        mods.append(ShieldDrone())
      elif mod_type == 'normaldrone':
        mods.append(NormalDrone())
      elif mod_type == 'overheat':
        mods.append(Overheat())
    return mods

  def compute(self, *args, **kwargs):
    ws = kwargs.get('ws')
    toughness = kwargs.get('toughness')
    strength = kwargs.get('strength')
    ap = kwargs.get('ap')
    save = kwargs.get('save')
    invuln = kwargs.get('invuln')
    fnp = kwargs.get('fnp')
    wounds = kwargs.get('wounds')
    shots = kwargs.get('shots')
    damage = kwargs.get('damage')
    shotmods = kwargs.get('shotmods')
    hitmods = kwargs.get('hitmods')
    woundmods = kwargs.get('woundmods')
    savemods = kwargs.get('savemods')
    fnpmods = kwargs.get('fnpmods')
    damagemods = kwargs.get('damagemods')

    modifiers = ModifierCollection()
    modifiers.add_mods('shots', self.parse_mods(shotmods))
    modifiers.add_mods('hit', self.parse_mods(hitmods))
    modifiers.add_mods('wound', self.parse_mods(woundmods))
    modifiers.add_mods('pen', self.parse_mods(savemods))
    modifiers.add_mods('fnp', self.parse_mods(fnpmods))
    modifiers.add_mods('damage', self.parse_mods(damagemods))

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
      shots=self.parse_rsn(shots or 1),
      strength=int(strength or 1),
      ap=int(ap or 0),
      damage=self.parse_rsn(damage or 1),
    )
    attack_sequence = AttackSequence(weapon, target, target, modifiers)
    return attack_sequence.run()

  def parse_rsn(self, value):
    try:
      return PMFCollection([PMF.static(int(value or 1))])
    except ValueError:
      match = re.match(r'(?P<number>\d+)?d(?P<faces>\d+)', value.lower())
      if match:
        number, faces = re.match(r'(?P<number>\d+)?d(?P<faces>\d+)', value.lower()).groups()
        return PMFCollection.mdn(int(number) if number else 1, int(faces))
      else:
        return PMFCollection.empty()


class URLMinify(object):
  def __init__(self, tab_count, weapon_count):
    self.tab_count = tab_count
    self.weapon_count = weapon_count
    self.mapping = [
      *self.data_row(),
      *self.target_row(),
      *self.attack_row(),
      *self.modify_row(),
    ]

  def minify(self, key):
    return self.to_min().get(key, key)

  def maxify(self, key):
    return self.to_max().get(key, key)

  def to_min(self):
    return {x:y for x, y in self.mapping}

  def to_max(self):
    return {y:x for x, y in self.mapping}

  def data_row(self):
    row = []
    for i in range(self.tab_count):
      row += self.data_row_input(i)
    return row

  def data_row_input(self, tab_id):
    return [
      [f'enabled_{tab_id}', f'e_{tab_id}'],
      [f'tabname_{tab_id}', f'tn_{tab_id}'],
    ]

  def target_row(self):
    row = []
    for i in range(self.tab_count):
      row += self.target_row_input(i)
    return row

  def target_row_input(self, tab_id):
    return [
      [f'toughness_{tab_id}', f't_{tab_id}'],
      [f'save_{tab_id}', f'sv_{tab_id}'],
      [f'invuln_{tab_id}', f'inv_{tab_id}'],
      [f'fnp_{tab_id}', f'fn_{tab_id}'],
      [f'wounds_{tab_id}', f'w_{tab_id}'],
    ]

  def attack_row(self):
    row = []
    for i in range(self.tab_count):
      for j in range(self.weapon_count):
        row += self.attack_row_input(i, j)
    return row

  def attack_row_input(self, tab_id, weapon_id):
    return [
      [f'weaponenabled_{tab_id}_{weapon_id}', f'we_{tab_id}_{weapon_id}'],
      [f'ws_{tab_id}_{weapon_id}', f'ws_{tab_id}_{weapon_id}'],
      [f'strength_{tab_id}_{weapon_id}', f's_{tab_id}_{weapon_id}'],
      [f'ap_{tab_id}_{weapon_id}', f'ap_{tab_id}_{weapon_id}'],
      [f'shots_{tab_id}_{weapon_id}', f'sh_{tab_id}_{weapon_id}'],
      [f'damage_{tab_id}_{weapon_id}', f'dm_{tab_id}_{weapon_id}'],
    ]

  def modify_row(self):
    row = []
    for i in range(self.tab_count):
      for j in range(self.weapon_count):
        row += self.modify_input(i, j)
    return row

  def modify_input(self, tab_id, weapon_id):
    return [
      [f'shotmods_{tab_id}_{weapon_id}', f'shm_{tab_id}_{weapon_id}'],
      [f'hitmods_{tab_id}_{weapon_id}', f'hm_{tab_id}_{weapon_id}'],
      [f'woundmods_{tab_id}_{weapon_id}', f'wm_{tab_id}_{weapon_id}'],
      [f'savemods_{tab_id}_{weapon_id}', f'svm_{tab_id}_{weapon_id}'],
      [f'fnpmods_{tab_id}_{weapon_id}', f'fnpm_{tab_id}_{weapon_id}'],
      [f'damagemods_{tab_id}_{weapon_id}', f'dmm_{tab_id}_{weapon_id}'],
    ]


class InputGenerator(object):
  def __init__(self, tab_count, weapon_count):
    self.tab_count = tab_count
    self.weapon_count = weapon_count

  def gen_tab_inputs(self, tab_id, weapon_count):
    return {
      **self.data_row_input(tab_id),
      **self.target_row_input(tab_id),
      **self.weapon_group_input(tab_id, weapon_count),
    }

  def data_row_input(self, tab_id):
    return {
      f'enabled_{tab_id}': 'value',
      f'tabname_{tab_id}': 'value',
    }

  def target_row_input(self, tab_id):
    return {
      f'toughness_{tab_id}': 'value',
      f'save_{tab_id}': 'value',
      f'invuln_{tab_id}': 'value',
      f'fnp_{tab_id}': 'value',
      f'wounds_{tab_id}': 'value',
    }

  def weapon_group_input(self, tab_id, weapon_count):
    output = {}
    for i in range(weapon_count):
      output.update(self.attack_row_input(tab_id, i))
      output.update(self.modify_input(tab_id, i))
    return output

  def attack_row_input(self, tab_id, weapon_id):
    return {
      f'weaponenabled_{tab_id}_{weapon_id}': 'value',
      f'ws_{tab_id}_{weapon_id}': 'value',
      f'strength_{tab_id}_{weapon_id}': 'value',
      f'ap_{tab_id}_{weapon_id}': 'value',
      f'shots_{tab_id}_{weapon_id}': 'value',
      f'damage_{tab_id}_{weapon_id}': 'value',
    }

  def modify_input(self, tab_id, weapon_id):
    return {
      f'shotmods_{tab_id}_{weapon_id}': 'value',
      f'hitmods_{tab_id}_{weapon_id}': 'value',
      f'woundmods_{tab_id}_{weapon_id}': 'value',
      f'savemods_{tab_id}_{weapon_id}': 'value',
      f'fnpmods_{tab_id}_{weapon_id}': 'value',
      f'damagemods_{tab_id}_{weapon_id}': 'value',
    }

  def graph_inputs(self):
    inputs = {'title': 'value'}
    for i in range(self.tab_count):
      inputs.update(self.gen_tab_inputs(i, self.weapon_count))
    return inputs
