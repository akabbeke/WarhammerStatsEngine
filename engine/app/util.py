import re
from warhammer_stats.attack import Attack
from warhammer_stats.pmf import PMF, PMFCollection
from warhammer_stats.weapon import Weapon
from warhammer_stats.target import Target
from warhammer_stats.modifiers import ModifierCollection


class ModifierController:
  @property
  def mod_dict(self):
    return {}

class ComputeController:
  def parse_mods(self, raw_mods):
    if not raw_mods:
      return []
    mods = []
    mod_dict = ModifierController().mod_dict
    for mod_id in raw_mods:
      mods.append(mod_dict.get(mod_id))
    return [mod for mod in mods if mod is not None]

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

    modifiers = ModifierCollection(
      shot_mods=self.parse_mods(shotmods),
      hit_mods=self.parse_mods(hitmods),
      wound_mods=self.parse_mods(woundmods),
      pen_mods=self.parse_mods(savemods),
      fnp_mods=self.parse_mods(fnpmods),
      damage_mods=self.parse_mods(damagemods),
    )

    target = Target(
      toughness=int(toughness or 1),
      save=int(save or 7),
      invuln=int(invuln or 7),
      fnp=int(fnp or 7),
      wounds=int(wounds or 1),
    )

    weapon = Weapon(
      bs=int(ws or 7),
      shots=self.parse_rsn(shots or 1),
      strength=int(strength or 1),
      ap=int(ap or 0),
      damage=self.parse_rsn(damage or 1),
      modifiers=modifiers,
    )

    attack_sequence = Attack(weapon=weapon, target=target)
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
      [f'points_{tab_id}', f'pts_{tab_id}'],
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
      f'points_{tab_id}': 'value',
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
