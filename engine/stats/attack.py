from .pmf import PMF, PMFCollection


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

  def _get_mod_extra_wound(self):
    return self._mods.get_mod_extra_wound()

  def _get_extra_wound(self):
    return self._mods.get_extra_wound()

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
    # Total hack for the thresh mod
    thresh_mod = self._mods.modify_hit_thresh(6) - 6

    # Handle extra hits
    hits_col = PMFCollection.add_many([
      self._get_mod_extra_hit().thresh_mod(thresh_mod),
      self._get_extra_hit(),
    ])
    if hits_col:
      dists.append(PMF.convolve_many([hits_col.mul_pmf(x) for x in dice_dists]))

    # Handle extra shots
    shots_col = PMFCollection.add_many([
      self._get_mod_extra_shot().thresh_mod(thresh_mod),
      self._get_extra_shot(),
    ])
    if shots_col:
      shot_dist = PMF.convolve_many([shots_col.mul_pmf(x) for x in dice_dists])
      hit_dist = self._calc_hit_dist(shot_dist, can_recurse=False)
      dists.append(hit_dist)

    return PMF.convolve_many(dists)

  def _calc_mortal_hit_dist(self, dice_dists):
    # Handle mortal_wounds
    # Total hack for the thresh mod
    thresh_mod = self._mods.modify_hit_thresh(6) - 6
    mortal_col = PMFCollection.add_many([
      self._get_hit_mod_mortal_wounds().thresh_mod(thresh_mod),
      self._get_hit_mortal_wounds(),
    ])
    if mortal_col:
      return PMF.convolve_many([mortal_col.mul_pmf(x) for x in dice_dists])
    else:
      return PMF.static(0)

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
      exp_dist = self._calc_exp_wound_dist(dice_dists)
      mortal_dist = self._calc_mortal_wound_dist(dice_dists)
      self._mortal_dists.append((mortal_dist * event_prob).rectify_zero())
      dists.append(PMF.convolve_many([wound_dist, exp_dist]) * event_prob)
    return PMF.flatten(dists)

  def _calc_exp_wound_dist(self, dice_dists):
    # Total hack for the thresh mod
    thresh_mod = self._mods.modify_wound_thresh(6) - 6

    # Handle extra wounds
    hits_col = PMFCollection.add_many([
      self._get_mod_extra_wound().thresh_mod(thresh_mod),
      self._get_extra_wound(),
    ])
    if hits_col:
      return PMF.convolve_many([hits_col.mul_pmf(x) for x in dice_dists])
    else:
      return PMF.static(0)

  def _calc_mortal_wound_dist(self, dice_dists):
    # Handle mortal_wounds
    thresh_mod =  self._mods.modify_wound_thresh(6) - 6
    mortal_col = PMFCollection.add_many([
      self._get_wound_mod_mortal_wounds().thresh_mod(thresh_mod),
      self._get_wound_mortal_wounds(),
    ])
    if mortal_col:
      return PMF.convolve_many([mortal_col.mul_pmf(x) for x in dice_dists])
    else:
      return PMF.static(0)

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
    self._shot_dist = self._calc_shots_dist()
    self._hit_dist = self._calc_hit_dist(self._shot_dist)
    self._wound_dist = self._calc_wound_dist(self._hit_dist)
    self._pen_dist = self._calc_pen_dist(self._wound_dist)
    self._damage_dist = self._calc_damage_dist(self._pen_dist)
    self._mortal_dist = PMF.convolve_many(self._mortal_dists)
    return PMF.convolve_many([self._damage_dist, self._mortal_dist])