from .pmf import PMF


class AttackSequence(object):
  """
  Generates the probability distribution for damage dealt from an attack sequence
  """
  def __init__(self, weapon, target, attacker, modifiers):
    self._weapon = weapon
    self._target = target
    self._attacker= attacker
    self._modifiers = modifiers

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
    shots = self._modifiers.modify_shot_dice(self._weapon.shots)
    return PMF.convolve_many(shots)

  def _calc_dice_dists(self, dist, dice_dist):
    dists = []
    for dice, event_prob in enumerate(dist.values):
      dists.append(PMF.convolve_many([dice_dist] * dice) * event_prob)
    return PMF.flatten(dists)

  def _calc_hit_dist(self, dist):
    return self._calc_dice_dists(dist, self._get_hit_dist())

  def _get_hit_dist(self):
    threshold = self._modifiers.modify_hit_thresh(self._attacker.ws)
    dice = self._modifiers.modify_hit_dice(PMF.dn(6), threshold)
    return dice.convert_binomial(threshold)

  def _calc_wound_dist(self, dist):
    return self._calc_dice_dists(dist, self._get_wound_dist())

  def _get_wound_dist(self):
    threshold = self._calc_wound_threshold(self._weapon.strength, self._target.toughness)
    dice = self._modifiers.modify_wound_dice(PMF.dn(6), threshold)
    threshold = self._modifiers.modify_wound_thresh(threshold)
    return dice.convert_binomial(threshold)

  def _calc_pen_dist(self, dist):
    return self._calc_dice_dists(dist, self._get_pen_prob())

  def _get_pen_prob(self):
    threshold = self._modifiers.modify_pen_thresh(
      self._target.save,
      self._weapon.ap,
      self._target.invuln
    )
    dice = self._modifiers.modify_pen_dice(PMF.dn(6), threshold)
    return dice.convert_binomial_less_than(threshold)

  def _calc_damage_dist(self, dist):
    individual_dist = self._calc_individual_damage_dist()
    damge_dists = []
    for dice, event_prob in enumerate(dist.values):
      damge_dists.append(PMF.convolve_many([individual_dist] * dice) * event_prob)
    return PMF.flatten(damge_dists)

  def _calc_individual_damage_dist(self):
    dice_dist = self._weapon.damage
    damage_dist = PMF.convolve_many(dice_dist)
    return damage_dist.ceiling(self._target.wounds)

  def run(self):
    shot_dist = self._calc_shots_dist()
    hit_dist = self._calc_hit_dist(shot_dist)
    wound_dist = self._calc_wound_dist(hit_dist)
    pen_dist = self._calc_pen_dist(wound_dist)
    damage_dist = self._calc_damage_dist(pen_dist)
    return damage_dist