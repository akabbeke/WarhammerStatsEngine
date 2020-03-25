import math
from numpy import fft, zeros


class PMF(object):
  """
  Discrete Probability Distribution - Used to keep track of the probability of random discrete events
  """
  def __init__(self, values=None):
    self.values = values if values is not None else []

  def __str__(self):
    return str(self.values)

  def __len__(self):
    return len(self.values)

  def __mul__(self, other):
    return PMF([other*x for x in self.values])

  def __rmul__(self, other):
    return self.__mul__(other)

  def __getitem__(self, key):
    if not isinstance(key, int):
      raise ValueError()
    if key < 0 or key >= len(self):
      return 0
    else:
      return self.values[key]

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
    return PMF([0.0] * min_val + [sum(self.values[:min_val+1])] + self.values[min_val+1:])

  def mean(self):
    return sum([x*p for x, p in enumerate(self.values)])

  def std(self):
    mean = self.mean()
    exp_mean = sum([(x**2)*p for x, p in enumerate(self.values)])
    return (exp_mean - mean**2)**(0.5)

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

class PMFCollection(object):
  """
  Discrete Probability Distribution - Used to keep track of collections of PMFs
  """
  def __init__(self, pmfs=None):
    self.pmfs = pmfs if pmfs is not None else []

  def __bool__(self):
    return len(self) > 0

  def __len__(self):
    return len(self.pmfs)

  def __str__(self):
    return str([x.values for x in self.pmfs])

  def get(self, index, defualt=None):
    try:
      return self.pmfs[index]
    except IndexError:
      return defualt

  def thresh_mod(self, thresh_mod):
    """
    Modify the collection based on a dice modifer
    """
    if thresh_mod == 0 or self.pmfs == []:
      return self
    elif thresh_mod > 0:
      return PMFCollection(self.pmfs[:1] * thresh_mod + self.pmfs)
    elif thresh_mod < 0:
      return PMFCollection((self.pmfs + self.pmfs[-1:] * (-1 * thresh_mod))[-1*len(self.pmfs):])

  def mul_col(self, col):
    return PMFCollection([self.mul_pmf(pmf) for pmf in col.pmfs])

  def mul_pmf(self, pmf):
    """
    Multiply the collection with a pmf and return a confolution of the results
    """
    new_pmfs = []
    for i, value in enumerate(pmf.values):
      new_pmfs.append(self.get(i, PMF.static(0)) * value)
    return PMF.flatten(new_pmfs)

  def convolve(self):
    return PMF.convolve_many(self.pmfs)

  def convert_binomial(self, thresh, less_than=False):
    if less_than:
      return self.map(lambda x: x.convert_binomial_less_than(thresh))
    else:
      return self.map(lambda x: x.convert_binomial(thresh))

  def map(self, func):
    return PMFCollection([func(x) for x in self.pmfs])

  @classmethod
  def add_many(cls, collection_list):
    new_pmfs = []
    for i in range(max([len(x) for x in collection_list] or [0])):
      new_pmfs.append(PMF.convolve_many([x.get(i, PMF.static(0)) for x in collection_list if x]))
    return PMFCollection(new_pmfs)

  @classmethod
  def empty(cls):
    return PMFCollection([])

  @classmethod
  def mdn(cls, m, n):
    return PMFCollection([PMF.dn(n)] * m)


