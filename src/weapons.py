from .pmf import  PMF

class Weapon(object):
  """
  Used to keep track of the params of the weapon
  """
  def __init__(self, shots, strength, ap, damage):
    self.shots = shots
    self.strength = strength
    self.ap = ap
    self.damage = damage

battle_cannon = Weapon(
  shots=[PMF.dn(6)],
  strength=8,
  ap=2,
  damage=[PMF.dn(3)],
)

relic_battle_cannon = Weapon(
  shots=[PMF.dn(6)],
  strength=8,
  ap=2,
  damage=[PMF.static(3)],
)

demolisher_cannon = Weapon(
  shots=[PMF.dn(6)],
  strength=10,
  ap=3,
  damage=[PMF.dn(6)],
)

nova_cannon = Weapon(
  shots=[PMF.dn(6)],
  strength=6,
  ap=2,
  damage=[PMF.dn(3)],
)

executioner_cannon = Weapon(
  shots=[PMF.dn(6)],
  strength=8,
  ap=3,
  damage=[PMF.static(2)],
)

auto_cannon = Weapon(
  shots=[PMF.static(4)],
  strength=7,
  ap=1,
  damage=[PMF.static(2)],
)

punisher_cannon = Weapon(
  shots=[PMF.static(20)],
  strength=5,
  ap=0,
  damage=[PMF.static(1)],
)

vanquisher_cannon = Weapon(
  shots=[PMF.static(1)],
  strength=8,
  ap=3,
  damage=[PMF.max_of_two(PMF.dn(6), PMF.dn(6))],
)

las_cannon = Weapon(
  shots=[PMF.static(1)],
  strength=9,
  ap=3,
  damage=[PMF.dn(6)],
)

plasma_cannon = Weapon(
  shots=[PMF.dn(3)],
  strength=8,
  ap=3,
  damage=[PMF.static(2)],
)

heavy_bolter = Weapon(
  shots=[PMF.static(3)],
  strength=5,
  ap=1,
  damage=[PMF.static(1)],
)

multi_melta = Weapon(
  shots=[PMF.static(1)],
  strength=8,
  ap=4,
  damage=[PMF.max_of_two(PMF.dn(6), PMF.dn(6))],
)

storm_cannon = Weapon(
  shots=[PMF.static(10)],
  strength=7,
  ap=2,
  damage=[PMF.static(2)],
)