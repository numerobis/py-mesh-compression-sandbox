from __future__ import division
import math

class gamma(object):
  def __str__(self): return "gamma"

  def bitlength(self, word):
      """
      Return the length of a naive gamma-coded version of 'word', which must be a signed int.

      Length is in unary zeroes.  '1' marks the first bit of the number.
      If there are no zeroes, the value is zero.
      Append a sign bit unless the value is zero.

      There's better encodings! E.g. huffman-code the lengths, so that 0
      (which isn't that common) doesn't get the shortest encoding.
      """
      if word == 0: return 1
      else: 
        wordLength = int(math.ceil(math.log(abs(word)) / math.log(2)))
        return 2 * wordLength + 1

class gammagamma(object):
  def __init__(self): self._gamma = gamma()

  def __str__(self): return "gamma-gamma"

  def bitlength(self, word):
      """
      Iterate on gamma encoding: first gamma-encode the length in bits.
      Then write the number, with a sign bit.
      """
      if word == 0: return 1
      else:
        # compute the length of the number. It's not zero.
        wordLength = int(math.ceil(math.log(abs(word)) / math.log(2)))
        # gamma-encode the length, but don't write the sign bit
        n = self._gamma.bitlength(wordLength) - 1
        # now write the number
        n += wordLength
        return n

class nibble(object):
  def __str__(self): return "nibble"

  def bitlength(self, word):
      """
      Return the length of a naive nibble-coded version of 'word', which must be a signed int.
      We have one nibble (4 bits) giving the number of nibbles to follow.
      0 => the value is zero.
      2 => 8 bits follow.
      15 => 64 bits follow (special case -- not 60!)
      One of those bits is a sign bit.
      """
      if word == 0:
        return 4
      nibblesNeeded = int(math.ceil(math.log(abs(word * 2)) / math.log(2**4)))
      if nibblesNeeded >= 15:
        nibblesNeeded = 16
      return (nibblesNeeded + 1) * 4

class variableword(object):
  def __str__(self): return "variable-word"

  def bitlength(self, word):
    """
    Try to fit in 8 bits; if that fails, encode FF and
    try to fit in 16 bits; if that fails, encode FFFF and
    try to fit in 32 bits; if that fails, encode FFFFFFFF and
    encode in 64 bits.

    When trying to fit in 16 bits, subtract off 127 (or -127) because we
    know it can't be a small value.
    """
    word = abs(word)
    if word <= 2**7 - 1:
      return 8
    word -= 2**7 - 1
    if word <= 2**15 - 1:
      return 8 + 16
    word -= 2**15 - 1
    if word <= 2**32 - 1:
      return 8 + 16 + 32
    return 8 + 16 + 32 + 64

class bytelong(object):
  def __str__(self): return "byte-or-long"

  def bitlength(self, word):
    """
    Return the length of a word encoded as either a byte if it fits, or a byte
    followed by a 64-bit int if it doesn't. The byte has value -128 if we need the long.
    """
    if word <= 127 and word >= -127:
      return 8
    else:
      return 8 + 64
