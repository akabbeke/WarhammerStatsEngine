class Unit(object):
  """
  Used to keep track of the params of the unit
  """
  def __init__(self, *args, **kwargs):
    self.ws = kwargs.get('ws', 7)
    self.bs = kwargs.get('bs', 7)
    self.toughness = kwargs.get('toughness', 1)
    self.save = kwargs.get('save', 7)
    self.invuln = kwargs.get('invul', 7)
    self.fnp = kwargs.get('fnp', 7)
    self.wounds = kwargs.get('wounds')
    self.weapons = kwargs.get('weapons')
    self.modifiers = kwargs.get('modifiers')

  def set_weapons(self, weapons):
    self.weapons = weapons

  def set_modifiers(self, modifiers):
    self.modifiers = modifiers


relic_leviathan = Unit(
  ws=2,
  bs=2,
  toughness=8,
  save=2,
  invul=4,
  wounds=14,
)

guardsmen = Unit(
  ws=4,
  bs=4,
  toughness=3,
  save=5,
  invul=7,
  wounds=1,
)

space_marine = Unit(
  ws=3,
  bs=3,
  toughness=4,
  save=3,
  invul=7,
  wounds=2,
)

terminator = Unit(
  ws=3,
  bs=3,
  toughness=4,
  save=2,
  invul=5,
  wounds=2,
)

custode = Unit(
  ws=2,
  bs=2,
  toughness=5,
  save=2,
  invul=3,
  wounds=3,
)

riptide = Unit(
  ws=4,
  bs=4,
  toughness=7,
  save=2,
  invul=3,
  wounds=14,
)

russ = Unit(
  ws=4,
  bs=4,
  toughness=8,
  save=3,
  invul=7,
  wounds=12,
)

tank_commander = Unit(
  ws=3,
  bs=3,
  toughness=8,
  save=3,
  invul=7,
  wounds=12,
)


knight = Unit(
  ws=4,
  bs=4,
  toughness=8,
  save=3,
  invul=4,
  wounds=24,
)

targets = {
  "GEQ": guardsmen,
  "MEQ": space_marine,
  "TEQ": terminator,
  "Custode": custode,
  "Riptide": riptide,
  "Russ": russ,
  "Knight": knight,
}