class Weapon(object):
  """
  Used to keep track of the params of the weapon
  """
  def __init__(self, shots, strength, ap, damage):
    self.shots = shots
    self.strength = strength
    self.ap = ap
    self.damage = damage