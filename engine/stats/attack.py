from .pmf import PMF, PMFCollection

class AttackTrace(object):
  def __init__(self, dist, mods):
    self.dist = dist
    self.mods = mods
    self.downstream = []


class AttackSequenceResults(object):
  def __init__(self, shot_dist, hit_dist, wound_dist, pen_dist, damage_dist, drone_wound, mortal_dist):
    self.shot_dist = shot_dist
    self.hit_dist = hit_dist
    self.wound_dist = wound_dist
    self.pen_dist = pen_dist
    self.damage_dist = damage_dist
    self.drone_wound = drone_wound
    self.mortal_dist = mortal_dist
    self.damage_with_mortals = PMF.convolve_many([
      self.damage_dist,
      self.mortal_dist,
    ])


class AttackSequence(object):
  """
  Generates the probability distribution for damage dealt from an attack sequence
  """
  def __init__(self, weapon, target, attacker, mods):
    self.weapon = weapon
    self.target = target
    self.attacker = attacker
    self.mods = mods

    self.shots = AttackShots(self)
    self.hits = AttackHits(self)
    self.wounds = AttackWounds(self)
    self.drones = AttackDrones(self)
    self.pens = AttackPens(self)
    self.damage = AttackDamage(self)

  def run(self):
    mortal_dists = []

    shot_dist = self.shots.calc_dist()

    hit_dist, mortal_dist = self.hits.calc_dist(shot_dist)
    mortal_dists.append(mortal_dist)

    wound_dist, mortal_dist = self.wounds.calc_dist(hit_dist)
    mortal_dists.append(mortal_dist)

    drone_pen, drone_wound = self.drones.calc_dist(wound_dist)

    pen_dist = self.pens.calc_dist(drone_pen)
    damage_dist = self.damage.calc_dist(pen_dist)

    return AttackSequenceResults(
      shot_dist,
      hit_dist,
      wound_dist,
      pen_dist,
      damage_dist,
      drone_wound,
      PMF.convolve_many(mortal_dists),
    )


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
      return dist_col.mul_col(dice_dists).convolve()
    else:
      return PMF.static(0)

  def _mod_extra_dist(self):
    return PMFCollection.empty()

  def _extra_dist(self):
    return PMFCollection.empty()

  def _calc_mortal_dist(self, dice_dists):
    dist_col = PMFCollection.add_many([
      self._mod_mortal_dist().thresh_mod(self.thresh_mod),
      self._mortal_dist(),
    ])
    if dist_col:
      return dist_col.mul_col(dice_dists).convolve()
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
    shots_dists = self.attack.mods.modify_shot_dice(self.attack.weapon.shots)
    return shots_dists.convolve()


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
      if event_prob == 0:
        continue
      dice_dists = self.attack.mods.modify_hit_dice(
        PMFCollection.mdn(dice, 6),
        thresh,
        mod_thresh
      )

      hit_dist = dice_dists.convert_binomial(mod_thresh).convolve()
      exp_dist = self._calc_exp_dist(dice_dists) if can_recurse else PMF([1])
      exp_shot_dist, exp_mrt_dist = self._calc_exp_shot_dist(dice_dists, can_recurse)
      mrt_dist = self._calc_mortal_dist(dice_dists)

      hit_dists.append(hit_dist * event_prob)
      exp_dists.append(PMF.convolve_many([exp_dist, exp_shot_dist]) * event_prob)
      mrt_dists.append(PMF.convolve_many([mrt_dist, exp_mrt_dist]) * event_prob)

    return PMF.convolve_many([PMF.flatten(hit_dists), PMF.flatten(exp_dists)]), PMF.flatten(mrt_dists)

  def _get_thresh_mod(self):
    return self.attack.mods.modify_hit_thresh(6) - 6

  def _calc_exp_shot_dist(self, dice_dists, can_recurse=True):
    # Handle extra shots
    if not can_recurse:
      return PMF.static(0), PMF.static(0)
    dist_col = PMFCollection.add_many([
      self._get_mod_extra_shot().thresh_mod(self.thresh_mod),
      self._get_extra_shot(),
    ])
    if dist_col:
      return self.calc_dist(dist_col.mul_col(dice_dists).convolve(), can_recurse=False)
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
      if event_prob == 0:
        continue
      dice_dists = self.attack.mods.modify_wound_dice(
        PMFCollection.mdn(dice, 6),
        thresh,
        mod_thresh
      )
      wnd_dist = dice_dists.convert_binomial(mod_thresh).convolve()
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


class AttackDrones(AttackSegment):
  """
  Generate the PMF for the penetrations
  """
  def calc_dist(self, dist):
    drone_enabled, drone_thresh, drone_fnp = self.attack.mods.modify_drone()

    if not drone_enabled:
      return dist, PMF.static(0)

    pens = []
    saves = []
    for dice, event_prob in enumerate(dist.values):
      if event_prob == 0:
        continue
      dice_dists = PMFCollection.mdn(dice, 6)
      pen_dist = dice_dists.convert_binomial(
        drone_thresh,
        less_than=True,
      ).convolve()
      save_dist = dice_dists.convert_binomial(
        drone_thresh,
      ).convolve()
      pens.append(pen_dist * event_prob)
      saves.append(save_dist * event_prob)

    return PMF.flatten(pens), self._calc_fnp_dist(PMF.flatten(saves), drone_fnp)

  def _calc_fnp_dist(self, dist, drone_fnp):
    dists = []
    for dice, event_prob in enumerate(dist.values):
      if event_prob == 0:
        continue
      dice_dists = PMFCollection.mdn(dice, 6)
      binom_dists = dice_dists.convert_binomial(drone_fnp, less_than=True).convolve()
      dists.append(binom_dists * event_prob)
    return PMF.flatten(dists)


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
      if event_prob == 0:
        continue
      dice_dists = self.attack.mods.modify_pen_dice(
        PMFCollection.mdn(dice, 6),
        mod_thresh,
        mod_thresh
      )
      pen_dists = dice_dists.convert_binomial(mod_thresh, less_than=True).convolve()
      dists.append(pen_dists * event_prob)
    return PMF.flatten(dists)


class AttackDamage(AttackSegment):
  """
  Generate the PMF for the damage
  """
  def calc_dist(self, dist):
    individual_dist = self._calc_individual_damage_dist()
    damge_dists = []
    for dice, event_prob in enumerate(dist.values):
      if event_prob == 0:
        continue
      damge_dists.append(PMF.convolve_many([individual_dist] * dice) * event_prob)
    return PMF.flatten(damge_dists)

  def _calc_individual_damage_dist(self):
    dice_dists = self.attack.weapon.damage
    mod_dists = self.attack.mods.modify_damage_dice(dice_dists)
    fnp_dist = self._calc_fnp_dist(mod_dists.convolve())
    return fnp_dist.ceiling(self.attack.target.wounds)

  def _calc_fnp_dist(self, dist):
    dists = []
    mod_thresh = self.attack.mods.modify_fnp_thresh(self.attack.target.fnp)
    for dice, event_prob in enumerate(dist.values):
      if event_prob == 0:
        continue
      dice_dists = self.attack.mods.modify_fnp_dice(
        PMFCollection.mdn(dice, 6),
        self.attack.target.fnp,
        mod_thresh,
      )
      binom_dists = dice_dists.convert_binomial(mod_thresh, less_than=True).convolve()
      dists.append(binom_dists * event_prob)
    return PMF.flatten(dists)


