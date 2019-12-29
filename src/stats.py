from .pmf import PMF


class AttackSequence(object):
  """
  Generates the probability distribution for damage dealt from an attack sequence
  """
  def __init__(self, weapon, target, attacker, mods):
    self._weapon = weapon
    self._target = target
    self._attacker= attacker
    self._mods = mods

  def _calc_wound_thresh(self, strength, toughness):
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
    shots = self._mods.modify_shot_dice(self._weapon.shots)
    return PMF.convolve_many(shots)

  def _calc_dice_dists(self, dist, dice_dist):
    dists = []
    for dice, event_prob in enumerate(dist.values):
      dists.append(PMF.convolve_many([dice_dist] * dice) * event_prob)
    return PMF.flatten(dists)

  def _calc_dist(self, dist, thresh, mod_thresh, mod):
    dists = []
    for dice, event_prob in enumerate(dist.values):
      dice_dists = mod([PMF.dn(6)] * dice, thresh, mod_thresh)
      binom_dists = [x.convert_binomial(mod_thresh) for x in dice_dists]
      dists.append(PMF.convolve_many(binom_dists) * event_prob)
    return PMF.flatten(dists)

  def _calc_less_than_dist(self, dist, thresh, mod_thresh, mod):
    dists = []
    for dice, event_prob in enumerate(dist.values):
      dice_dists = mod([PMF.dn(6)] * dice, thresh, mod_thresh)
      binom_dists = [x.convert_binomial_less_than(mod_thresh) for x in dice_dists]
      dists.append(PMF.convolve_many(binom_dists) * event_prob)
    return PMF.flatten(dists)

  def _calc_hit_dist(self, dist):
    return self._calc_dist(
      dist,
      self._attacker.ws,
      self._mods.modify_hit_thresh(self._attacker.ws),
      self._mods.modify_hit_dice,
    )

  def _calc_wound_dist(self, dist):
    thresh = self._calc_wound_thresh(
      self._weapon.strength,
      self._target.toughness
    )
    return self._calc_dist(
      dist,
      thresh,
      self._mods.modify_wound_thresh(thresh),
      self._mods.modify_wound_dice
    )

  def _calc_pen_dist(self, dist):
    mod_thresh = self._mods.modify_pen_thresh(
      self._target.save,
      self._weapon.ap,
      self._target.invuln
    )
    return self._calc_less_than_dist(
      dist,
      mod_thresh,
      mod_thresh,
      self._mods.modify_pen_dice
    )

  def _calc_damage_dist(self, dist):
    individual_dist = self._calc_individual_damage_dist()
    damge_dists = []
    for dice, event_prob in enumerate(dist.values):
      damge_dists.append(PMF.convolve_many([individual_dist] * dice) * event_prob)
    return PMF.flatten(damge_dists)

  def _calc_individual_damage_dist(self):
    dice_dist = self._weapon.damage
    mod_dist = self._mods.modify_damage_dice(dice_dist)
    damage_dist = PMF.convolve_many(mod_dist)
    fnp_dist = self._calc_fnp_dist(damage_dist)
    return fnp_dist.ceiling(self._target.wounds)

  def _calc_fnp_dist(self, dist):
    return self._calc_less_than_dist(
      dist,
      self._target.fnp,
      self._mods.modify_fnp_thresh(self._target.fnp),
      self._mods.modify_fnp_dice
    )

  def run(self):
    shot_dist = self._calc_shots_dist()
    hit_dist = self._calc_hit_dist(shot_dist)
    wound_dist = self._calc_wound_dist(hit_dist)
    pen_dist = self._calc_pen_dist(wound_dist)
    damage_dist = self._calc_damage_dist(pen_dist)

    return damage_dist