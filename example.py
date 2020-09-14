import matplotlib.pyplot as plt
import numpy as np

from engine.stats.pmf import PMF, PMFCollection
from engine.stats.units import Unit
from engine.stats.weapons import Weapon
from engine.stats.attack import AttackSequence
from engine.stats.modifiers import ReRollFailed, ModifierCollection
def main():

  weapon = Weapon(
    shots=PMFCollection.static(450),
    strength=3,
    ap=0,
    damage=PMFCollection.static(1),
  )

  target = Unit(
    toughness=3,
    save=5,
    wounds=1,
  )

  attacker = Unit(ws=4)

  attack = AttackSequence(
    weapon=weapon,
    target=target,
    attacker=attacker,
    mods=ModifierCollection()
  ).run()

  print(attack.damage_dist.mean())





if __name__ == "__main__":
  main()
