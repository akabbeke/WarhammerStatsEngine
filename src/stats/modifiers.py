from .pmf import PMF, PMFCollection

class Modifier(object):
  """
  Base class for Modifiers. 'priority' is used for order of opperations and
  for re-rolls it determines the which re-roll is applied.
  e.g. full re-roll > re-roll failed > re-roll 1s
  """
  priority = 0
  def __init__(self, *args, **kwargs):
    pass

  def modify_dice(self, dists, thresh=None,  mod_thresh=None):
    return dists

  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    return dists

  def modify_threshold(self, thresh):
    return thresh

  def modify_save(self, save):
    return save

  def modify_ap(self, ap):
    return ap

  def modify_invuln(self, invuln):
    return invuln

  def mod_extra_hit(self):
    return None

  def extra_hit(self):
    return None

  def mod_extra_shot(self):
    return None

  def extra_shot(self):
    return None

  def mod_extra_wound(self):
    return None

  def extra_wound(self):
    return None

  def mod_mortal_wound(self):
    return None

  def mortal_wound(self):
    return None


class MinimumValue(Modifier):
  def __init__(self, min_val):
    self.min_val = min_val

  def modify_dice(self, dists, thresh=None,  mod_thresh=None):
    return [x.min(self.min_val) for x in dists]


class ExplodingDice(Modifier):
  def __init__(self, thresh, value):
    self.thresh = max(0, min(7, thresh))
    self.value = value

  def _pmf_collection(self):
    return PMFCollection([PMF.static(0)] * self.thresh + [PMF.static(self.value)] * (7 - self.thresh))


class ModExtraHit(ExplodingDice):
  def mod_extra_hit(self):
    return self._pmf_collection()


class ExtraHit(ExplodingDice):
  def extra_hit(self):
    return self._pmf_collection()


class ModExtraShot(ExplodingDice):
  def mod_extra_shot(self):
    return self._pmf_collection()


class ExtraShot(ExplodingDice):
  def extra_shot(self):
    return self._pmf_collection()


class ModExtraWound(ExplodingDice):
  def mod_extra_wound(self):
    return self._pmf_collection()


class ExtraWound(ExplodingDice):
  def extra_wound(self):
    return self._pmf_collection()


class GenerateMortalWound(ExplodingDice):
  def mortal_wound(self):
    return self._pmf_collection()


class ModGenerateMortalWound(ExplodingDice):
  def mod_mortal_wound(self):
    return self._pmf_collection()


class Haywire(ExplodingDice):
  def mod_mortal_wound(self):
    col = [PMF.static(0), PMF.static(0), PMF.static(0), PMF.static(0), PMF.static(1), PMF.static(1), PMF.dn(3)]
    return PMFCollection(col)


class ReRollOnes(Modifier):
  priority = 1
  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    return [x.re_roll_value(1) for x in dists]


class ReRollFailed(Modifier):
  priority = 99
  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    return [x.re_roll_less_than(min(thresh, mod_thresh)) for x in dists]

class ReRollOneDice(Modifier):
  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    if not dists:
      return dists
    dists[0] = dists[0].re_roll_less_than(thresh)
    return dists

class ModReRollOneDice(Modifier):
  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    if not dists:
      return dists
    dists[0] = dists[0].re_roll_less_than(mod_thresh)
    return dists

class ReRollOneDiceVolume(Modifier):
  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    if not dists:
      return dists
    dists[0] = dists[0].re_roll_less_than(dists[0].expected_value())
    return dists

class ReRollAll(Modifier):
  priority = 100
  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    return [x.re_roll_less_than(mod_thresh) for x in dists]


class ReRollLessThanExpectedValue(Modifier):
  priority = 98
  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    return [x.re_roll_less_than(x.expected_value()) for x in dists]


class Melta(Modifier):
  def modify_dice(self, dists, thresh=None, mod_thresh=None):
    return [x.melta() for x in dists]


class AddNTo(Modifier):
  def __init__(self, value=0, *args, **kwargs):
    self.n = value
    self.priority = self.n


class AddNToThreshold(AddNTo):
  def modify_threshold(self, thresh):
    return thresh - self.n


class AddNToAP(AddNTo):
  def modify_ap(self, ap):
    return ap - self.n


class AddNToSave(AddNTo):
  def modify_save(self, save):
    return save - self.n


class AddNToInvuln(AddNTo):
  def modify_invuln(self, invuln):
    return invuln - self.n


class AddNToVolume(AddNTo):
  def modify_dice(self, dists, thresh=None, mod_thresh=None):
    return [x.roll(self.n) for x in dists]

class AddD6(AddNTo):
  def modify_dice(self, dists, thresh=None, mod_thresh=None):
    dists.append(PMF.dn(6))
    return dists

class AddD3(AddNTo):
  def modify_dice(self, dists, thresh=None, mod_thresh=None):
    dists.append(PMF.dn(3))
    return dists

class SetToN(Modifier):
  def __init__(self, value=0, *args, **kwargs):
    self.n = value


class SetThresholdToN(SetToN):
  def modify_threshold(self, thresh):
    return self.n


class SetAPToN(SetToN):
  def modify_ap(self, ap):
    return self.n


class SetSaveToN(SetToN):
  def modify_save(self, save):
    return self.n


class SetInvulnToN(SetToN):
  def modify_invuln(self, invuln):
    return self.n


class IgnoreAP(Modifier):
  def __init__(self, value=0, *args, **kwargs):
    self.ap = value

  def modify_ap(self, ap):
    return 0 if ap <= self.ap else ap


class IgnoreInvuln(Modifier):
  def modify_invuln(self, ap):
    return 7


class HalfDamage(Modifier):
  def modify_dice(self, dists, thresh=None, mod_thresh=None):
    return [x.div_min_one(2) for x in dists]


class ModifierCollection(object):
  """
  Used to keep track of any modifiers to the attack
  """
  def __init__(self, data=None):
    self._data = {'shots': [], 'hit': [], 'wound': [], 'pen': [], 'fnp': [], 'damage': []}
    self.merge_dicts(data or {})

  def merge_dicts(self, mod_dict):
    for mod_name in self._data:
      self._data[mod_name] += mod_dict.get(mod_name, [])
    self._sort_modifiers()

  def add_mods(self, mod_name, mods):
    self._data[mod_name] += mods

  def _sort_modifiers(self):
    for mod_name in self._data:
      self._data[mod_name] = sorted(
        self._data[mod_name],
        key=lambda x: x.priority,
        reverse=True
      )

  def _shot_mods(self):
    return self._data.get('shots', [])

  def _hit_mods(self):
    return self._data.get('hit', [])

  def _wound_mods(self):
    return self._data.get('wound', [])

  def _pen_mods(self):
    return self._data.get('pen', [])

  def _fnp_mods(self):
    return self._data.get('fnp', [])

  def _damage_mods(self):
    return self._data.get('damage', [])

  def _get_mods(self, mods_name):
    return self._data.get(mods_name, [])

  def _mod_dice(self, dists, mods, thresh=None, mod_thresh=None):
    """
    Apply dice modifications. Rerolls happen before modifiers.
    """
    for mod in mods:
      dists = mod.modify_re_roll(dists, thresh, mod_thresh)
    for mod in mods:
      dists = mod.modify_dice(dists, thresh, mod_thresh)
    return dists

  def modify_shot_dice(self, dists):
    """
    Modify the PMF of shot volume the dice. Ususally for re-rolls.
    """
    return self._mod_dice(dists, self._shot_mods())

  def modify_hit_thresh(self, thresh):
    """
    Modify the hit threshold. Important to note the -1 to hit modifiers actually
    are a +1 to the threshold. Similarly +1 to hits are -1 to the threshold.
    """
    if thresh == 1:
      # Handle the case where the weapon is auto hit. No to hit modifiers apply
      return thresh
    for mod in self._hit_mods():
      thresh = mod.modify_threshold(thresh)
    return max(thresh, 2) #1's always fail

  def modify_hit_dice(self, dists, thresh, mod_thresh):
    """
    Modify the PMF of hit dice. Ususally for re-rolls.
    """
    return self._mod_dice(dists, self._hit_mods(), thresh, mod_thresh)

  def modify_wound_thresh(self, thresh):
    """
    Modify the wound threshold. Important to note the -1 to wound modifiers actually
    are a +1 to the threshold. Similarly +1 are -1 to the threshold.
    """
    for mod in self._wound_mods():
      thresh = mod.modify_threshold(thresh)
    return max(2, thresh) # 1's always fail

  def modify_wound_dice(self, dists, thresh, mod_thresh):
    """
    Modify the PMF of hit dice. Ususally for re-rolls.
    """
    return self._mod_dice(dists, self._wound_mods(), thresh, mod_thresh)

  def modify_pen_thresh(self, save, ap, invuln):
    """
    Modify the pen threshold by modifying the save, ap, and invuln
    """
    for mod in self._pen_mods():
      save = mod.modify_save(save)
    for mod in self._pen_mods():
      ap = mod.modify_ap(ap)
    for mod in self._pen_mods():
      invuln = mod.modify_invuln(invuln)
    return min(max(save + ap, 2), max(invuln, 2)) # 1's alwasys fail

  def modify_pen_dice(self, dists, thresh, mod_thresh):
    """
    Modify the PMF of the pen dice. Ususally for re-rolls.
    """
    return self._mod_dice(dists, self._pen_mods(), thresh, mod_thresh)

  def modify_fnp_thresh(self, thresh):
    """
    Modify the fnp threshold. I think some death guard units can do this?
    """
    for mod in self._fnp_mods():
      thresh = mod.modify_threshold(thresh)
    return max(thresh, 2) # 1's alwasys fail

  def modify_fnp_dice(self, dists, thresh, mod_thresh):
    """
    Modify the PMF of the FNP dice. Ususally for re-rolls.
    """
    return self._mod_dice(dists, self._fnp_mods(), thresh, mod_thresh)

  def modify_damage_dice(self, dists):
    """
    Modify the damage dice
    """
    return self._mod_dice(dists, self._damage_mods())

  def sum_generators(self, mod_list, attr_name):
    cols = [getattr(mod, attr_name)() for mod in mod_list]
    cols = [x for x in cols if x]
    return PMFCollection.add_many(cols)

  def get_mod_extra_hit(self):
    """
    Generate extra hits on a modfiable value
    """
    return self.sum_generators(self._hit_mods(), 'mod_extra_hit')

  def get_extra_hit(self):
    """
    Generate extra hits on a static value
    """
    return self.sum_generators(self._hit_mods(), 'extra_hit')

  def get_mod_extra_shot(self):
    """
    Generate extra shots on a modfiable value
    """
    return self.sum_generators(self._hit_mods(), 'mod_extra_shot')

  def get_extra_shot(self):
    """
    Generate extra shots on a static value
    """
    return self.sum_generators(self._hit_mods(), 'extra_shot')

  def get_mod_extra_wound(self):
    """
    Generate extra wounds on a modfiable value
    """
    return self.sum_generators(self._wound_mods(), 'mod_extra_wound')

  def get_extra_wound(self):
    """
    Generate extra wounds on a static value
    """
    return self.sum_generators(self._wound_mods(), 'extra_wound')

  def get_mod_mortal_wounds(self, mods_name):
    """
    Generate mortal wounds on a modfiable value
    """
    return self.sum_generators(self._get_mods(mods_name), 'mod_mortal_wound')

  def get_mortal_wounds(self, mods_name):
    """
    Generate mortal wounds on a static value
    """
    return self.sum_generators(self._get_mods(mods_name), 'mortal_wound')
