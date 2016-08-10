from __future__ import division

import math

# A 'mapping' permutes indices in [0..n) via the [] operator, and it has a name via str()

class identity(object):
  def __getitem__(self, index): return index
  def __str__(self): return "identity"

class array_mapping(object):
  def __init__(self, array, name):
        self._array = array
        self._name = name
  def __getitem__(self, index): return self._array[index]
  def __str__(self): return self._name

def morton(points):
  """
  The implementation is to order according to Morton-order: interleave the bits. 
  I use the full precision to do this.
  Notionally we see doubles as being signed integers of length 53+2**13 bits.
  """
  # implementation adapted from http://compgeom.com/~piyush/papers/tvcg_stann.pdf
  def msdb(ma, mb):
    """
    Returns the index of the most significant differing bit.
    Returns 53 if the mantissas are equal.

    Ignores the sign.
    """
    x = int(abs(ma)) ^ int(abs(mb))
    r = 0
    while x > 0:
      r += 1
      x = x >> 1
    return r

  def xormsb(a, b):
    """
    Notionally, expand a and b from doubles to very long integers.

    Return the MSB where they differ, counting from 0 = the position of the
    implicit bit in the smallest normalized number. May return a value as small
    as -53.

    If the values differ in sign, return a very large MSB.
    """
    # sort negative before positive
    if (a < 0) != (b < 0):
        # return a bit position larger than the largest double
        # how much larger doesn't matter.
        return 2**20
    (ea, ma) = math.frexp(a)
    (eb, mb) = math.frexp(b)
    msb = max(ea, eb)
    if ea == eb:
      # same exponent, how far down the mantissa do we go?
      msb -= msdb(ma, mb)
    return msb

  def morton_compare(apoint, bpoint):
    compare = 0
    largest_msdb = -100
    for a,b in zip(apoint, bpoint):
      msdb = xormsb(a,b)
      if msdb > largest_msdb:
        largest_msdb = msdb
        compare = cmp(a,b)
    assert largest_msdb > -100
    return compare

  def morton_compare_index(aindex, bindex):
    return morton_compare(points[aindex], points[bindex])

  index_map = list(range(len(points)))
  index_map.sort(cmp = morton_compare_index)
  return array_mapping(index_map, "morton")
