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
