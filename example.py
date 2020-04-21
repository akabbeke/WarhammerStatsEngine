import matplotlib.pyplot as plt
import numpy as np

from engine.stats.pmf import PMF

def main():

  print(PMF.dn(3).std(), PMF.dn(3).mean())
  print(PMF.static(3).std(), PMF.static(3).mean())



if __name__ == "__main__":
  main()
