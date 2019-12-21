import matplotlib.pyplot as plt
import numpy as np

from src.stats import Target, Attack, Modifiers, AttackSequence, RSN, DPD


def main():
  guardsmen = Target(
    toughness=3,
    save=5,
    invul=7,
    wounds=1,
  )

  space_marine = Target(
    toughness=4,
    save=3,
    invul=7,
    wounds=2,
  )

  terminator = Target(
    toughness=4,
    save=2,
    invul=5,
    wounds=2,
  )

  custode = Target(
    toughness=5,
    save=2,
    invul=3,
    wounds=3,
  )

  riptide = Target(
    toughness=7,
    save=2,
    invul=3,
    wounds=14,
  )

  russ = Target(
    toughness=8,
    save=3,
    invul=7,
    wounds=12,
  )

  knight = Target(
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


  ws = 3

  battle_cannon = Attack(
    shots=RSN(dice=2, faces=6),
    ws=ws,
    strength=8,
    ap=2,
    damage=RSN(dice=1, faces=3),
  )

  demolisher_cannon = Attack(
    shots=RSN(dice=2, faces=6),
    ws=ws,
    strength=10,
    ap=3,
    damage=RSN(dice=1, faces=6),
  )

  nova_cannon = Attack(
    shots=RSN(dice=2, faces=6),
    ws=ws,
    strength=6,
    ap=2,
    damage=RSN(dice=1, faces=3),
  )

  plasma_cannon = Attack(
    shots=RSN(dice=2, faces=6),
    ws=ws,
    strength=8,
    ap=3,
    damage=RSN(static=2),
  )

  auto_cannon = Attack(
    shots=RSN(static=8),
    ws=ws,
    strength=7,
    ap=1,
    damage=RSN(static=2),
  )

  punisher_cannon = Attack(
    shots=RSN(static=40),
    ws=ws,
    strength=5,
    ap=0,
    damage=RSN(static=1),
  )

  weapons = {
    'Battle Cannon': battle_cannon,
    'Demolisher Cannon': demolisher_cannon,
    'Nova Cannon': nova_cannon,
    'Plasma Cannon': plasma_cannon,
    'Auto Cannon': auto_cannon,
    'Punisher Cannon': punisher_cannon,
  }

  dists = {}
  for name, target in targets.items():
    dists[name] = AttackSequence(
      attack=plasma_cannon,
      target=target,
      modifiers=Modifiers(),
    ).run(trim_tail=True)
  print(dists)
  plot_line_distros(dists)


def plot_line_distros(distros):
  ticks = []
  for bar_name, values in distros.items():
    ticks += [i for i, x in enumerate(values)]
    plt.plot(
      [i for i, x in enumerate(values)],
      [100*x for i, x in enumerate(values)],
      label=bar_name,
    )

  plt.legend()
  plt.xlabel('damage')
  plt.ylabel('probability')
  plt.xticks(np.arange(min(ticks), max(ticks)+1, 1.0))
  plt.yticks(np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]))
  plt.title('Probability')
  plt.grid()
  plt.show()


def plot_bar_distro(distros):
  ticks = []
  for bar_name, values in distros.items():
    ticks += [i for i, x in enumerate(values)]
    plt.bar(
      [i for i, x in enumerate(values)],
      [100*x for i, x in enumerate(values)],
      label=bar_name,
    )

  plt.legend()
  plt.xlabel('damage')
  plt.ylabel('probability')
  plt.xticks(np.arange(min(ticks), max(ticks)+1, 1.0))
  plt.yticks(np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]))
  plt.title('Probability')
  plt.grid()
  plt.show()


if __name__ == "__main__":
  main()
