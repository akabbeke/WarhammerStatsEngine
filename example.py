import matplotlib.pyplot as plt
import numpy as np

from engine.stats.pmf import PMF

def main():
  pmf = PMF.dn(6).re_roll_less_than(4)
  rrpmf = pmf.convert_binomial_less_than(4)
  print(rrpmf.values)



if __name__ == "__main__":
  main()
