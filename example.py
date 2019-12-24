import matplotlib.pyplot as plt
import numpy as np

from src.stats import AttackSequence
from src.pmf import PMF
from src.weapons import relic_battle_cannon, battle_cannon, demolisher_cannon, punisher_cannon
from src.units import guardsmen, space_marine, tank_commander, knight
from src.modifiers import Modifiers
from src.plots import plot_line_distros

def main():

  basic = AttackSequence(
    punisher_cannon,
    knight,
    tank_commander,
    Modifiers(),
  )
  cadia = AttackSequence(
    punisher_cannon,
    knight,
    tank_commander,
    Modifiers(hit_re_roll='re_roll_1s'),
  )

  catachan = AttackSequence(
    punisher_cannon,
    knight,
    tank_commander,
    Modifiers(shot_modifier='re_roll_one_dice'),
  )

  dists = {
    "basic": basic.run().cumulative().trim_tail().values,
    "cadia": cadia.run().cumulative().trim_tail().values,
    "catachan": catachan.run().cumulative().trim_tail().values,
  }

  plot_line_distros(dists)



if __name__ == "__main__":
  main()
