from .pmf import PMF, PMFCollection


class AttackSequence(object):
  """
  Generates the probability distribution for damage dealt from an attack sequence
  """
  def __init__(self, weapon, target, attacker, mods):
    self.weapon = weapon
    self.target = target
    self.attacker= attacker
    self.mods = mods

    self.shots = AttackShots(self)
    self.hits = AttackHits(self)
    self.wounds = AttackWounds(self)
    self.pens = AttackPens(self)
    self.damage = AttackDamage(self)

  def run(self):
    mortal_dists = []

    shot_dist = self.shots.calc_dist()
    hit_dist, mortal_dist = self.hits.calc_dist(shot_dist)
    mortal_dists.append(mortal_dist)

    wound_dist, mortal_dist = self.wounds.calc_dist(hit_dist)
    mortal_dists.append(mortal_dist)

    pen_dist = self.pens.calc_dist(wound_dist)
    damage_dist = self.damage.calc_dist(pen_dist)

    return PMF.convolve_many([damage_dist,  PMF.convolve_many(mortal_dists)])


class AttackSegment(object):
  def __init__(self, attack):
    self.attack = attack
    self._thresh_mod = None

  def calc_dist(self):
    pass

  @property
  def thresh_mod(self):
    if self._thresh_mod is None:
      self._thresh_mod = self._get_thresh_mod()
    return self._thresh_mod

  def _get_thresh_mod(self):
    return 0

  def _calc_exp_dist(self, dice_dists):
    dist_col = PMFCollection.add_many([
      self._mod_extra_dist().thresh_mod(self.thresh_mod),
      self._extra_dist(),
    ])

    if dist_col:
      return PMF.convolve_many([dist_col.mul_pmf(x) for x in dice_dists])
    else:
      return PMF.static(0)

  def _mod_extra_dist(self):
    return PMFCollection.empty()

  def _extra_dist(self):
    return PMFCollection.empty()

  def _calc_mortal_dist(self, dice_dists):
    mortal_col = PMFCollection.add_many([
      self._mod_mortal_dist().thresh_mod(self.thresh_mod),
      self._mortal_dist(),
    ])
    if mortal_col:
      return PMF.convolve_many([mortal_col.mul_pmf(x) for x in dice_dists])
    else:
      return PMF.static(0)

  def _mod_mortal_dist(self):
    return PMFCollection.empty()

  def _mortal_dist(self):
    return PMFCollection.empty()


class AttackShots(AttackSegment):
  """
  Generate the PMF for the number of shots
  """
  def calc_dist(self):
    shots = self.attack.mods.modify_shot_dice(self.attack.weapon.shots)
    return PMF.convolve_many(shots)


class AttackHits(AttackSegment):
  """
  Generate the PMF for the hits
  """
  def calc_dist(self, dist, can_recurse=True):
    hit_dists = []
    exp_dists = []
    mrt_dists = []
    thresh = self.attack.attacker.ws
    mod_thresh = self.attack.mods.modify_hit_thresh(self.attack.attacker.ws)
    for dice, event_prob in enumerate(dist.values):
      dice_dists = self.attack.mods.modify_hit_dice(
        [PMF.dn(6)] * dice,
        thresh,
        mod_thresh
      )

      hit_dist = PMF.convolve_many([x.convert_binomial(mod_thresh) for x in dice_dists])
      exp_dist = self._calc_exp_dist(dice_dists) if can_recurse else PMF([1])
      exp_shot_dist, exp_mrt_dist = self._calc_exp_shot_dist(dice_dists)
      mrt_dist = self._calc_mortal_dist(dice_dists)

      hit_dists.append(hit_dist * event_prob)
      exp_dists.append(PMF.convolve_many([exp_dist, exp_shot_dist]) * event_prob)
      mrt_dists.append(PMF.convolve_many([mrt_dist, exp_mrt_dist]) * event_prob)

    return PMF.convolve_many([PMF.flatten(hit_dists), PMF.flatten(exp_dists)]), PMF.flatten(mrt_dists)

  def _get_thresh_mod(self):
    return self.attack.mods.modify_hit_thresh(6) - 6

  def _calc_exp_shot_dist(self, dice_dists):
    # Handle extra shots
    shots_col = PMFCollection.add_many([
      self._get_mod_extra_shot().thresh_mod(self.thresh_mod),
      self._get_extra_shot(),
    ])
    if shots_col:
      shot_dist = PMF.convolve_many([shots_col.mul_pmf(x) for x in dice_dists])
      return self.calc_dist(shot_dist, can_recurse=False)
    else:
      return PMF.static(0), PMF.static(0)

  def _mod_extra_dist(self):
    return self.attack.mods.get_mod_extra_hit()

  def _extra_dist(self):
    return self.attack.mods.get_extra_hit()

  def _get_mod_extra_shot(self):
    return self.attack.mods.get_mod_extra_shot()

  def _get_extra_shot(self):
    return self.attack.mods.get_extra_shot()

  def _mod_mortal_dist(self):
    return self.attack.mods.get_mod_mortal_wounds('hit')

  def _mortal_dist(self):
    return self.attack.mods.get_mortal_wounds('hit')


class AttackWounds(AttackSegment):
  """
  Generate the PMF for the wounds
  """
  def calc_dist(self, dist):
    wnd_dists = []
    exp_dists = []
    mrt_dists = []

    thresh = self._calc_wound_thresh(
      self.attack.weapon.strength,
      self.attack.target.toughness
    )
    mod_thresh = self.attack.mods.modify_wound_thresh(thresh)
    for dice, event_prob in enumerate(dist.values):
      dice_dists = self.attack.mods.modify_wound_dice(
        [PMF.dn(6)] * dice,
        thresh,
        mod_thresh
      )
      wnd_dist = PMF.convolve_many([x.convert_binomial(mod_thresh) for x in dice_dists])
      exp_dist = self._calc_exp_dist(dice_dists)
      mrt_dist = self._calc_mortal_dist(dice_dists)

      wnd_dists.append(wnd_dist * event_prob)
      exp_dists.append(exp_dist * event_prob)
      mrt_dists.append(mrt_dist * event_prob)
    return PMF.convolve_many([PMF.flatten(wnd_dists), PMF.flatten(exp_dists)]), PMF.flatten(mrt_dists)

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

  def _get_thresh_mod(self):
    return self.attack.mods.modify_wound_thresh(6) - 6

  def _mod_extra_dist(self):
    return self.attack.mods.get_mod_extra_wound()

  def _extra_dist(self):
    return self.attack.mods.get_extra_wound()

  def _mod_mortal_dist(self):
    return self.attack.mods.get_mod_mortal_wounds('wound')

  def _mortal_dist(self):
    return self.attack.mods.get_mortal_wounds('wound')


class AttackPens(AttackSegment):
  """
  Generate the PMF for the penetrations
  """
  def calc_dist(self, dist):
    mod_thresh = self.attack.mods.modify_pen_thresh(
      self.attack.target.save,
      self.attack.weapon.ap,
      self.attack.target.invuln
    )

    dists = []
    for dice, event_prob in enumerate(dist.values):
      dice_dists = self.attack.mods.modify_pen_dice(
        [PMF.dn(6)] * dice,
        mod_thresh,
        mod_thresh
      )
      binom_dists = [x.convert_binomial_less_than(mod_thresh) for x in dice_dists]
      dists.append(PMF.convolve_many(binom_dists) * event_prob)
    return PMF.flatten(dists)


class AttackDamage(AttackSegment):
  """
  Generate the PMF for the damage
  """
  def calc_dist(self, dist):
    individual_dist = self._calc_individual_damage_dist()
    damge_dists = []
    for dice, event_prob in enumerate(dist.values):
      damge_dists.append(PMF.convolve_many([individual_dist] * dice) * event_prob)
    return PMF.flatten(damge_dists)

  def _calc_individual_damage_dist(self):
    dice_dist = self.attack.weapon.damage
    mod_dist = self.attack.mods.modify_damage_dice(dice_dist)
    damage_dist = PMF.convolve_many(mod_dist)
    fnp_dist = self._calc_fnp_dist(damage_dist)
    return fnp_dist.ceiling(self.attack.target.wounds)

  def _calc_fnp_dist(self, dist):
    dists = []
    mod_thresh = self.attack.mods.modify_fnp_thresh(self.attack.target.fnp)
    for dice, event_prob in enumerate(dist.values):
      dice_dists = self.attack.mods.modify_fnp_dice(
        [PMF.dn(6)] * dice,
        self.attack.target.fnp,
        mod_thresh,
      )
      binom_dists = [x.convert_binomial_less_than(mod_thresh) for x in dice_dists]
      dists.append(PMF.convolve_many(binom_dists) * event_prob)
    return PMF.flatten(dists)


