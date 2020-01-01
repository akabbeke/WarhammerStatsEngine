import math
from numpy import fft, zeros


class PMF(object):
  """
  Discrete Probability Distribution - Used to keep track of the probability of random discrete events
  """
  def __init__(self, values=None):
    self.values = values if values is not None else []

  def __len__(self):
    return len(self.values)

  def __mul__(self, other):
    return PMF([other*x for x in self.values])

  def __rmul__(self, other):
    return self.__mul__(other)

  def ceiling(self, value):
    """
    Sum the probability of all values >= the ceiling value
    """
    new_values = []
    for i, prob in enumerate(self.values):
      if i <= value:
        new_values.append(prob)
      else:
        new_values[value] += prob
    return PMF(new_values)

  def trim_tail(self, thresh=10**(-4)):
    """
    Trim the long tail off where p < threshold
    """
    in_body = False
    trimmed_dist = []
    for element in self.values[::-1]:
      if in_body or element >= thresh:
        in_body = True
        trimmed_dist.append(element)
    return PMF(trimmed_dist[::-1])

  def cumulative(self):
    """
    Probability of at least each value
    """
    cumu_dist = []
    for i in range(len(self.values)):
      cumu_dist.append(sum(self.values[i:]))
    return PMF(cumu_dist)

  def re_roll_value(self, value):
    """
    Re-roll a specific value (eg re-roll 1's)
    """
    rr_mask = [0.0 if x == value else 1.0 for x in range(len(self))]
    rr_dist = [self.values[value] * x for x in self.values]
    new_dist = []
    for i, prob in enumerate(self.values):
      new_dist.append(rr_mask[i]*prob + rr_dist[i])
    return PMF(new_dist)

  def re_roll_less_than(self, value):
    """
    Re-roll all values below a specific value
    """

    rr_mask = [0.0 if i < value else x for i, x in enumerate(self.values)]

    for i, x in enumerate(self.values):
      if i < value:
        for j, y in enumerate(self.values):
          rr_mask[j] += self.values[i] * self.values[j]
    return PMF(rr_mask)

  def convert_binomial(self, thresh):
    return PMF([sum(self.values[:thresh]), sum(self.values[thresh:])])

  def convert_binomial_less_than(self, thresh):
    return PMF([sum(self.values[thresh:]), sum(self.values[:thresh])])

  def get(self, value):
    if value < 0:
      return 0
    if value > len(self.values):
      return 0
    else:
      return self.values[value]

  def expand_to(self, length):
    return PMF(self.values + [0.0] * max(length - len(self), 0))

  def expected_value(self):
    return sum([x*p for x, p in enumerate(self.values)])

  def add_value(self, n):
    return PMF([0.0] * n + self.values)

  def melta(self):
    return PMF.max_of_two(self, self)

  def roll(self, n):
    if n == 0:
      return self
    elif n > 0:
      return PMF([0.0] * n + self.values)
    else:
      return PMF([sum(self.values[:(-1*n)+1])] + self.values[(-1*n)+1:])

  def div_min_one(self, divisor):
    new_dist = [0.0] * len(self.values)
    for i, value in enumerate(self.values):
      new_dist[math.ceil(i/divisor)] += value
    return PMF(new_dist)

  def rectify_zero(self):
    new_dist = [1.0 - sum(self.values[1:])] + self.values[1:]
    return PMF(new_dist)

  def min(self, min_val):
    values = self.expand_to(min_val).values
    return PMF([0.0] * min_val + [sum(self.values[:min_val+1])] + self.values[min_val+1:])

  @classmethod
  def dn(cls, n):
    return PMF([0.0] + [1/n] * n)

  @classmethod
  def static(cls, n):
    return PMF([0.0] * n + [1.0])

  @classmethod
  def convolve_many(cls, dists):
    """
    Convolve a list of 1d float arrays together, using FFTs.
    The arrays need not have the same length, but each array should
    have length at least 1.
    """
    result_length = 1 + sum((len(dist) - 1) for dist in dists)

    # Copy each array into a 2d array of the appropriate shape.
    rows = zeros((len(dists), result_length))
    for i, dist in enumerate(dists):
        rows[i, :len(dist)] = dist.values

    # Transform, take the product, and do the inverse transform
    # to get the convolution.
    fft_of_rows = fft.fft(rows)
    fft_of_convolution = fft_of_rows.prod(axis=0)
    convolution = fft.ifft(fft_of_convolution)

    # Assuming real inputs, the imaginary part of the output can
    # be ignored.
    return PMF(convolution.real)

  @classmethod
  def flatten(cls, dists):
    """
    Sum a set of distributions to produce a new distribution.
    """
    flat_dist = [0.0] * (max([len(dist) for dist in dists]))
    for dist in dists:
      for i, value in enumerate(dist.values):
        flat_dist[i] += value
    return PMF(flat_dist)

  @classmethod
  def match_sizes(cls, dists):
    """
    Map a set of PMFs to the same size
    """
    largest = max([len(x) for x in dists])
    return [x.expand_to(largest) for x in dists]

  @classmethod
  def max_of_two(cls, dist1, dist2):
    """
    Compute the PMF for the max of two PMF
    """
    dist1, dist2 = cls.match_sizes([dist1, dist2])
    new_dist = []
    for value in range(len(dist1)):
      prob = dist1.get(value) * dist2.get(value)
      prob += dist1.values[value] * sum(dist2.values[:value])
      prob += dist2.values[value] * sum(dist1.values[:value])
      new_dist.append(prob)
    return PMF(new_dist)

