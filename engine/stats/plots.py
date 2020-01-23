import matplotlib.pyplot as plt
import numpy as np

def plot_line_distros(distros):
  ticks = []
  max_prob = 0
  for bar_name, values in distros.items():
    ticks += [i for i, x in enumerate(values)]
    max_prob = max(max_prob, max([100*x for i, x in enumerate(values)]))
    plt.plot(
      [i for i, x in enumerate(values)],
      [100*x for i, x in enumerate(values)],
      label=bar_name,
    )

  plt.legend()
  plt.xlabel('damage')
  plt.ylabel('probability')
  plt.xticks(np.arange(min(ticks), max(ticks)+1, 1.0))
  plt.yticks(np.array(list(range(0,round(int(max_prob),-1)+10,10))))
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

