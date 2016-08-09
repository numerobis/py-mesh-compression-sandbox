#! /usr/bin/python
from __future__ import division

import sys
import re
import math

import mapping
from mapping import identity_mapping, morton_mapping

import fileinput
from fileinput import ply_file

def bitlength(quantized):
  """
  Return the length of a naive gamma-coded version of 'quantized':

  Length is in unary zeroes. If there are no zeroes, the value is zero.
  '1' marks the first bit of the number.
  Append a sign bit.
  => 2 + log2(abs(quantized), or 1 bit for 0.

  There's better encodings! E.g. huffman-code the lengths, so that 0
  (which is uncommon) doesn't get the shortest encoding.
  """
  if quantized == 0: return 1
  else: return 2 + int(math.ceil(math.log(abs(quantized)) / math.log(2)))

def encode_geometry(points, index_map, quantum=1e-6):
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
  for p in [ pt for index,pt in sorted(zip(index_map, points)) ]:
    quantum = [ int(round(x * invQuantum)) for x in p ]
    diffQuantum = [ x-y for (x,y) in zip(quantum, lastQuantum) ]
    lastQuantum = quantum
    # stats
    sumQuantum = [ x + abs(y) for (x,y) in zip(sumQuantum, diffQuantum) ]
    sumBits = [ x + bitlength(y) for (x,y) in zip(sumBits, diffQuantum) ]
    maxQuantum = [ max(x,abs(y)) for (x,y) in zip(maxQuantum, diffQuantum) ]
    n += 1

  nBytes = int(math.ceil(sum(sumBits)))
  print ("{} points\n  max diff: {}\n  avg diff: {}\n  avg bits: {}\n  total bytes geometry: {:,}".format(
         n, 
         ', '.join( ("{:,}".format(x)) for x in maxQuantum),
         ', '.join( ("%.2f" % (x/n)) for x in sumQuantum),
         ', '.join( ("%.4f" % (x/n)) for x in sumBits),
         nBytes
        ))

  return nBytes

def encode_topology(faces, index_map):
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
        for index in f:
          index = index_map[index]
          diff = index - lastIndex
          lastIndex = index
          sumBits += bitlength(diff)
          sumDiff += abs(diff)
          nDiff += 1
          maxDiff = max(maxDiff, abs(diff))
    print "printed {} {}-faces".format(nFaces, length)

  nBytes = int(math.ceil(sumBits / 8))
  print "{} faces, {} indices\n  max diff: {:,}\n  avg diff: {:2}\n  avg bits: {:,}\n  total bytes topology: {:,}".format(
         len(faces), nDiff, maxDiff, sumDiff / nDiff, sumBits / nDiff, nBytes
  )
  return nBytes

###########################################################################

data = ply_file(sys.argv[1])
print "opened %s; got %d points and %d faces" % (sys.argv[1], len(data.points), len(data.faces))

for mapping in (identity_mapping(), morton_mapping(data.points)):
    nBytes = 0
    nBytes += encode_geometry(data.points, mapping)
    nBytes += encode_topology(data.faces, mapping)
    print "{}: total of {:,} bytes, {} per vertex".format(str(mapping), nBytes, nBytes / len(data.points))
