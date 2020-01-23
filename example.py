import matplotlib.pyplot as plt
import numpy as np

from src.stats.pmf import PMF

def main():
  pmfs = [PMF.dn(6), PMF.dn(6)]
  print(PMF.convolve_many(pmfs).values)



if __name__ == "__main__":
  main()
