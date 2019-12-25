class Modifiers(object):
  """
  Used to keep track of any modifiers to the attack
  """
  def __init__(self, *args, **kwargs):
    self._shot_modifier = kwargs.get('shot_modifier')
    self._hit_re_roll = kwargs.get('hit_re_roll')
    self._hit_modifier = kwargs.get('hit_modifier', 0)
    self._wound_re_roll = kwargs.get('wound_re_roll')
    self._wound_modifier = kwargs.get('wound_modifier', 0)
    self._damage_re_roll = kwargs.get('damage_re_roll')
    self._damage_modifier = kwargs.get('damage_modifier', 0)


  def modify_shot_dice(self, dists):
    if self._shot_modifier == 're_roll_one_dice':
      dists[0] = dists[0].re_roll_less_than(dists[0].expected_value())
    elif self._shot_modifier == 're_roll_1s':
      dists = [x.re_roll_value(1) for x in dists]
    if self._shot_modifier == 're_roll_dice':
      dists = [x.re_roll_less_than(x.expected_value()) for x in dists]
    return dists

  def modify_hit_dice(self, dist, thresh):
    modified_thresh = self.modify_hit_thresh(thresh)
    return self.modify_roll(self._hit_re_roll, dist, thresh, modified_thresh)

  def modify_hit_thresh(self, thresh):
    return min(thresh + self._hit_modifier, 7)

  def modify_wound_dice(self, dist, thresh):
    modified_thresh = self.modify_wound_thresh(thresh)
    return self.modify_roll(self._wound_re_roll, dist, thresh, modified_thresh)

  def modify_wound_thresh(self, thresh):
    return min(thresh + self._wound_modifier, 7)

  def modify_pen_dice(self, dist, thresh):
    return dist

  def modify_pen_thresh(self, save, ap, invuln):
    return min(save + ap, invuln)

  def modify_roll(self, re_roll_type, dist, thresh, modified_thresh):
    # Re-rolls happen before modifiers but you don't have to re-roll
    # failed dice that would pass with a positive modifier
    lower_bound_thresh = min(thresh, modified_thresh)
    if re_roll_type == 're_roll_1s':
      return dist.re_roll_value(1)
    elif re_roll_type == 're_roll_failed':
      return dist.re_roll_less_than(lower_bound_thresh)
    elif re_roll_type == 're_roll':
      return dist.re_roll_less_than(modified_thresh)
    else:
      return dist

  def modify_fnp_thresh(self, thresh):
    return thresh

  def modify_fnp_dice(self, dist, thresh):
    return dist

  def modify_damage_dice(self, dists):
    if self._damage_re_roll == 'roll_two_choose_highest':
      dists = [x.melta() for x in dists]
    elif self._damage_re_roll == 're_roll_one_dice':
      dists[0] = dists[0].re_roll_less_than(dists[0].expected_value())
    elif self._damage_re_roll == 're_roll_1s':
      dists = [x.re_roll_value(1) for x in dists]
    elif self._damage_re_roll == 're_roll_dice':
      dists = [x.re_roll_less_than(x.expected_value()) for x in dists]
    dists = [x.roll(self._damage_modifier) for x in dists]
    return dists

