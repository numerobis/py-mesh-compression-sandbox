from __future__ import division

import re

# A file object has points and faces.
# Points is a list of 3-tuples.
# Faces is a list of n-tuples in CCW order. The tuples are indices into the points list.
#       A triangle is a 3-tuple, a quad is a 4-tuple, etc.

class ply_file(object):
  def __init__(self, filename):
    self.points = []
    self.faces = []
    with open(filename) as infile:
      # Parse the header
      npoints = 0
      nfaces = 0
      for line in infile:
        line = re.sub(r'\s*#.*','', line)
        if len(line) == 0:
          continue
        m = re.match('element (vertex|face) ([0-9]+)', line)
        if m:
          if m.group(1) == 'vertex':
            npoints = int(m.group(2))
          elif m.group(1) == 'face':
            nfaces = int(m.group(2))
        elif line.startswith("end_header"):
          break

      # Parse the main body
      for line in infile:
        line = re.sub(r'\s*#.*','', line)
        if len(line) == 0:
          continue
        elif len(self.points) < npoints:
          data = line.split()
          self.points.append( tuple(float(x) for x in data[0:3]) )
        else:
          data = line.split()
          self.faces.append( tuple(int(x) for x in data[1:]) )
