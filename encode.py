from __future__ import division

import math

class binary_stl(object):
  def __str__(self): return "binary STL"

  def encode_geometry(self, points):
    """
    STL doesn't encode points as a phase.
    """
    return 0

  def encode_topology(self, faces):
    # header: 80 bytes empty, followed by 32-bit count
    nBits = 80 * 8 + 32
    # foreach triangle: normal & 3 points then uint16 set to 0; each coordinate is 3 floats
    for f in faces:
      # how many triangles in this face? 3 points: 1; 4 points: 2; n points: n-2
      nTriangles = len(f) - 2
      nBits += nTriangles * (4 * 3 * 32 + 16)
    return int(math.ceil(nBits / 8))

###########################################################################

class difference(object):
  def __init__(self, intcoder, mapping):
    self._coder = intcoder
    self._index_map = mapping

  def __str__(self): return 'difference/' + str(self._index_map) + '/' + str(self._coder)

  def encode_geometry(self, points, quantum = 1e-6):
    """
    Difference-encode the geometry. Returns bytes written.

    Prints how much space it would take (doesn't actually encode it).

    Points is a list of 3-tuples (or something that iterates like that).

    Quantum is the minimum distance that we care about. For example, if your unit
    is meters, the default of 1e-6 means we will round to the nearest micron.

    A quantum of zero doesn't work.

    TODO: a negative quantum should mean we use an automatically adaptive quantum.
    """
    lastQuantum = (0,0,0)
    invQuantum = 1.0 / quantum

    # stats
    sumQuantum = (0,0,0)
    sumBits = (0,0,0)
    maxQuantum = (0,0,0)
    n = 0
    for p in [ pt for index,pt in sorted(zip(self._index_map, points)) ]:
      quantum = [ int(round(x * invQuantum)) for x in p ]
      diffQuantum = [ x-y for (x,y) in zip(quantum, lastQuantum) ]
      lastQuantum = quantum
      # stats
      sumQuantum = [ x + abs(y) for (x,y) in zip(sumQuantum, diffQuantum) ]
      sumBits = [ x + self._coder.bitlength(y) for (x,y) in zip(sumBits, diffQuantum) ]
      maxQuantum = [ max(x,abs(y)) for (x,y) in zip(maxQuantum, diffQuantum) ]
      n += 1

    nBytes = int(math.ceil(sum(sumBits) / 8))
    print ("**** {}".format(self))
    print ("  {} points\n\tmax diff: {}\n\tavg diff: {}\n\tavg bits: {}\n\ttotal bytes geometry: {:,}".format(
           n, 
           ', '.join( ("{:,}".format(x)) for x in maxQuantum),
           ', '.join( ("%.2f" % (x/n)) for x in sumQuantum),
           ', '.join( ("%.4f" % (x/n)) for x in sumBits),
           nBytes
          ))

    return nBytes

  def encode_topology(self, faces):
    """
    Encoding: first all the triangles, then all the quads, etc.
    Each section is:
     verts per face; number of indices ; list of indices (diff-encoded)
    The indices of 'faces' are reordered according to the indexMap.
    """
    sumBits = 0
    sumDiff = 0
    nDiff = 0
    maxDiff = 0
    faceLengths = dict()
    bitlength = self._coder.bitlength
    for f in faces:
      if len(f) in faceLengths:
          faceLengths[len(f)] += 1
      else: 
          faceLengths[len(f)] = 1

    for length in sorted(faceLengths.keys()):
      sumBits += bitlength(length) + bitlength(faceLengths[length])
      lastIndex = 0
      nFaces = 0
      for f in faces:
        if len(f) == length:
          nFaces += 1
          fmapped = [ self._index_map[index] for index in f ]
          for index in fmapped:
            diff = index - lastIndex
            lastIndex = index
            sumBits += bitlength(diff)
            sumDiff += abs(diff)
            nDiff += 1
            maxDiff = max(maxDiff, abs(diff))
      print "  printed {} {}-faces".format(nFaces, length)

    nBytes = int(math.ceil(sumBits / 8))
    print "  {} faces, {} indices\n\tmax diff: {:,}\n\tavg diff: {:2}\n\tavg bits: {:,}\n\ttotal bytes topology: {:,}".format(
           len(faces), nDiff, maxDiff, sumDiff / nDiff, sumBits / nDiff, nBytes
    )
    return nBytes
