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


class ReRollOnes(Modifier):
  priority = 1
  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    return [x.re_roll_value(1) for x in dists]


class ReRollFailed(Modifier):
  priority = 99
  def modify_re_roll(self, dists, thresh=None, mod_thresh=None):
    return [x.re_roll_less_than(min(thresh, mod_thresh)) for x in dists]


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


class RemoveInvuln(Modifier):
  def __init__(self, *args, **kwargs):
    self.ap = kwargs.get('ap', 0)

  def modify_invuln(self, ap):
    return 7


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
    for mod in self._hit_mods():
      thresh = mod.modify_threshold(thresh)
    return thresh

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
      thresh = mod.modify_save(thresh)
    for mod in self._pen_mods():
      ap = mod.modify_ap(ap)
    for mod in self._pen_mods():
      thresh = mod.modify_invuln(thresh)
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
