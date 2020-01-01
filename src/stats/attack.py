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
    self._shot_dist = None
    self._hit_dist = None
    self._wound_dist = None
    self._pen_dist = None
    self._damage_dist = None
    self._mortal_dists = []
    self._mortal_dist = []

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

  def _calc_hit_dist(self, dist, can_recurse=True):
    dists = []
    thresh = self._attacker.ws
    mod_thresh = self._mods.modify_hit_thresh(self._attacker.ws)
    for dice, event_prob in enumerate(dist.values):
      dice_dists = self._mods.modify_hit_dice([PMF.dn(6)] * dice, thresh, mod_thresh)
      hit_dist = PMF.convolve_many([x.convert_binomial(mod_thresh) for x in dice_dists])
      exp_dist = self._calc_exp_hit_dist(dice_dists) if can_recurse else PMF([1])
      mortal_dist = self._calc_mortal_hit_dist(dice_dists)
      self._mortal_dists.append((mortal_dist * event_prob).rectify_zero())
      dists.append(PMF.convolve_many([hit_dist, exp_dist]) * event_prob)
    return PMF.flatten(dists)

  def _get_mod_extra_hit(self):
    return self._mods.get_mod_extra_hit()

  def _get_extra_hit(self):
    return self._mods.get_extra_hit()

  def _get_mod_extra_shot(self):
    return self._mods.get_mod_extra_shot()

  def _get_extra_shot(self):
    return self._mods.get_extra_shot()

  def _get_hit_mod_mortal_wounds(self):
    return self._mods.get_mod_mortal_wounds('hit')

  def _get_hit_mortal_wounds(self):
    return self._mods.get_mortal_wounds('hit')

  def _get_wound_mod_mortal_wounds(self):
    return self._mods.get_mod_mortal_wounds('wound')

  def _get_wound_mortal_wounds(self):
    return self._mods.get_mortal_wounds('wound')

  def _convolve_dists(self, dist, dice_dist):
    value_dists = []
    for dice, event_prob in enumerate(dist.values):
      value_dists.append(PMF.convolve_many([dice_dist] * dice) * event_prob)
    return PMF.flatten(value_dists)

  def _calc_exp_hit_dist(self, dice_dists):
    dists = []
    # Handle modifiable extra hits
    for thresh, value in self._get_mod_extra_hit():
      mod_thresh = self._mods.modify_hit_thresh(thresh)
      exp_dist = PMF.convolve_many([x.convert_binomial(mod_thresh) for x in dice_dists])
      dists.append(self._convolve_dists(exp_dist, PMF.static(value)))

    # Handle static extra hits
    for thresh, value in self._get_extra_hit():
      exp_dist = PMF.convolve_many([x.convert_binomial(thresh) for x in dice_dists])
      dists.append(self._convolve_dists(exp_dist, PMF.static(value)))

    # Handle modifiable extra shots
    for thresh, value in self._get_mod_extra_shot():
      mod_thresh = self._mods.modify_hit_thresh(thresh)
      exp_dist = PMF.convolve_many([x.convert_binomial(mod_thresh) for x in dice_dists])
      shot_dist = self._convolve_dists(exp_dist, PMF.static(value))
      hit_dist = self._calc_hit_dist(shot_dist, can_recurse=False)
      dists.append(hit_dist)

    # Handle static extra shots
    for thresh, value in self._get_extra_shot():
      exp_dist = PMF.convolve_many([x.convert_binomial(thresh) for x in dice_dists])
      shot_dist = self._convolve_dists(exp_dist, PMF.static(value))
      hit_dist = self._calc_hit_dist(shot_dist, can_recurse=False)
      dists.append(hit_dist)

    return PMF.convolve_many(dists)

  def _calc_mortal_hit_dist(self, dice_dists):
    mortal_dists = []
    # Handle modifiable mortal_wounds
    for thresh, value in self._get_hit_mod_mortal_wounds():
      mod_thresh = self._mods.modify_hit_thresh(thresh)
      mortal_dist = PMF.convolve_many([x.convert_binomial(mod_thresh) for x in dice_dists])
      mortal_dists.append(self._convolve_dists(mortal_dist, PMF.static(value)))

    # Handle static mortal_wounds
    for thresh, value in self._get_hit_mortal_wounds():
      mortal_dist = PMF.convolve_many([x.convert_binomial(thresh) for x in dice_dists])
      mortal_dists.append(self._convolve_dists(mortal_dist, PMF.static(value)))

    return PMF.convolve_many(mortal_dists)

  def _calc_wound_dist(self, dist):
    dists = []
    thresh = self._calc_wound_thresh(
      self._weapon.strength,
      self._target.toughness
    )
    mod_thresh = self._mods.modify_wound_thresh(thresh)
    for dice, event_prob in enumerate(dist.values):
      dice_dists = self._mods.modify_wound_dice([PMF.dn(6)] * dice, thresh, mod_thresh)
      wound_dist = PMF.convolve_many([x.convert_binomial(mod_thresh) for x in dice_dists])
      mortal_dist = self._calc_mortal_wound_dist(dice_dists)
      self._mortal_dists.append((mortal_dist * event_prob).rectify_zero())
      dists.append(wound_dist * event_prob)
    return PMF.flatten(dists)

  def _calc_mortal_wound_dist(self, dice_dists):
    mortal_dists = []
    # Handle modifiable mortal_wounds
    for thresh, value in self._get_wound_mod_mortal_wounds():
      mod_thresh = self._mods.modify_hit_thresh(thresh)
      mortal_dist = PMF.convolve_many([x.convert_binomial(mod_thresh) for x in dice_dists])
      mortal_dists.append(self._convolve_dists(mortal_dist, PMF.static(value)))

    # Handle static mortal_wounds
    for thresh, value in self._get_wound_mortal_wounds():
      mortal_dist = PMF.convolve_many([x.convert_binomial(thresh) for x in dice_dists])
      mortal_dists.append(self._convolve_dists(mortal_dist, PMF.static(value)))
    return PMF.convolve_many(mortal_dists)

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
    print(damage_dist.values)
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
    self._shot_dist = self._calc_shots_dist()
    # print(self._shot_dist.values)
    self._hit_dist = self._calc_hit_dist(self._shot_dist)
    # print(self._hit_dist.values)
    self._wound_dist = self._calc_wound_dist(self._hit_dist)
    # print(self._wound_dist.values)
    self._pen_dist = self._calc_pen_dist(self._wound_dist)
    # print(self._pen_dist.values)
    self._damage_dist = self._calc_damage_dist(self._pen_dist)
    # print(self._damage_dist.values)
    self._mortal_dist = PMF.convolve_many(self._mortal_dists)
    # print(self._mortal_dist.values)
    return PMF.convolve_many([self._damage_dist, self._mortal_dist])