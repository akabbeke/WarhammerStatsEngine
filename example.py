import matplotlib.pyplot as plt
import numpy as np

from engine.stats.pmf import PMF

def main():
  toughness = 8
  pmfs = [PMF.dn(6), PMF.dn(6)]
  conv = PMF.convolve_many(pmfs)
  print(conv)
  bino = conv.convert_binomial(8)
  print(bino)
  fran = PMF([bino[0]] + [0]*5 + [bino[1]])
  for i in range(1,7):
    print(fran.convert_binomial(i))
  print(fran)




if __name__ == "__main__":
  main()
