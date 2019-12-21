import functools
import math

from numpy.polynomial.polynomial import Polynomial
from numpy import fft, zeros
from scipy.stats import binom


class DPD(object):
  """
  Discrete Probability Distribution - Used to keep track of the probability of random discrete events
  """
  def __init__(self, values=None):
    self.values = values if values is not None else []

  def __len__(self):
    return len(self.values)

  def __mul__(self, other):
    return DPD([other*x for x in self.values])

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
    return DPD(new_values)

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
    return DPD(trimmed_dist[::-1])

  def cumulative(self):
    """
    Probability of at least each value
    """
    cumu_dist = []
    for i in range(len(self.values)):
      cumu_dist.append(sum(self.values[i:]))
    return DPD(cumu_dist)

  @classmethod
  def dn(self, n):
    return DPD([0.0] + [1/n] * n)

  @classmethod
  def static(self, n):
    return DPD([0.0] * n + [1.0])

  @classmethod
  def convolve_many(self, dists):
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
    return DPD(convolution.real)

  @classmethod
  def flatten(self, dists):
    """
    Sum a set of distributions to produce a new distribution.
    """
    flat_dist = [0.0] * (max([len(dist) for dist in dists]))
    for dist in dists:
      for i, value in enumerate(dist.values):
        flat_dist[i] += value
    return DPD(flat_dist)


class RSN(object):
  """
  Random Static Number - In the rules several stats can be static or random. this
  abrtacts that away
  """
  def __init__(self, static=None, dice=None, faces=None):
    self.static = static
    self.dice = dice
    self.faces = faces
    self._dists = None

  @property
  def dists(self):
    if not self._dists:
      self._dists = self._get_dists()
    return self._dists

  def _get_dists(self):
    if self.static:
      return [DPD.static(self.static)]
    else:
      return [DPD.dn(self.faces)] * self.dice


class Attack(object):
  """
  Used to keep track of the params of the atacker
  """
  def __init__(self, shots, ws, strength, ap, damage):
    self.shots = shots
    self.ws = ws
    self.strength = strength
    self.ap = ap
    self.damage = damage


class Target(object):
  """
  Used to keep track of the params of the target
  """
  def __init__(self, toughness, save, invul, wounds):
    self.toughness = toughness
    self.save = save
    self.invuln = invul
    self.wounds = wounds


class Modifiers(object):
  """
  Used to keep track of any modifiers to the attack
  """
  def __init__(self, re_roll_hits=None, re_roll_wounds=None):
    self._re_roll_hits = re_roll_hits
    self._re_roll_wounds = re_roll_wounds

  def modify_hit_roll(self, prob):
    if self._re_roll_hits == 're_roll_1s':
      return (7/6) * prob
    elif self._re_roll_hits == 're_roll':
      return 2*prob-prob**2
    else:
      return prob

  def modify_wound_roll(self, prob):
    if self._re_roll_wounds == 're_roll_1s':
      return (7/6) * prob
    elif self._re_roll_wounds == 're_roll':
      return 2*prob-prob**2
    else:
      return prob


class AttackSequence(object):
  """
  Generates the probability distribution for damage dealt from an attack sequence
  """
  def __init__(self, attack, target, modifiers):
    self._attack = attack
    self._target = target
    self._modifiers = modifiers
    self._result_cache = {}

  def _dice_distro(self, n, p):
    distro = binom(n, p)
    return DPD([distro.pmf(x) for x in range(n+1)])

  def _calc_wound_threshold(self, strength, toughness):
    if strength <= toughness/2.0:
      return 6
    elif strength >= toughness*2:
      return 2
    elif toughness > strength:
      return 5
    elif toughness == strength:
      return 4
    else:
      return 3

  def _calc_shots_dist(self):
    return DPD.convolve_many(self._attack.shots.dists)

  def _calc_dice_dists(self, dist, dice_prob):
    dists = []
    for dice, event_prob in enumerate(dist.values):
      dists.append(event_prob * self._dice_distro(dice, dice_prob))
    return DPD.flatten(dists)

  def _calc_hit_dist(self, dist):
    return self._calc_dice_dists(dist, self._get_hit_prob())

  def _get_hit_prob(self):
    prob = max(7-self._attack.ws, 0)/6
    modified_prob = self._modifiers.modify_hit_roll(prob)
    return modified_prob

  def _calc_wound_dist(self, dist):
    return self._calc_dice_dists(dist, self._get_wound_prob())

  def _get_wound_prob(self):
    threshold = self._calc_wound_threshold(
      self._attack.strength,
      self._target.toughness
    )
    prob = max(7-threshold, 0)/6
    modified_prob = self._modifiers.modify_wound_roll(prob)
    return modified_prob

  def _calc_pen_dist(self, dist):
    return self._calc_dice_dists(dist, self._get_pen_prob())

  def _get_pen_prob(self):
    return 1 - max(7-min(self._target.save+self._attack.ap, self._target.invuln), 0)/6

  def _calc_damage_dist(self, dist):
    individual_dist = self._calc_individual_damage_dist()
    damge_dists = []
    for dice, event_prob in enumerate(dist.values):
      damge_dists.append(DPD.convolve_many([individual_dist] * dice) * event_prob)
    return DPD.flatten(damge_dists)

  def _calc_individual_damage_dist(self):
    dice_dist = self._attack.damage.dists
    damage_dist = DPD.convolve_many(dice_dist)
    return damage_dist.ceiling(self._target.wounds)

  def run(self, trim_tail=False):
    shot_dist = self._calc_shots_dist()
    hit_dist = self._calc_hit_dist(shot_dist)
    wound_dist = self._calc_wound_dist(hit_dist)
    pen_dist = self._calc_pen_dist(wound_dist)
    damage_dist = self._calc_damage_dist(pen_dist)
    damage_dist = damage_dist.cumulative()
    if trim_tail:
      return damage_dist.trim_tail().values
    else:
      return damage_dist.values
