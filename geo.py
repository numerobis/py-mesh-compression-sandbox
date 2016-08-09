#! /usr/bin/python
from __future__ import division

import sys
import re
import math

import mapping
import fileinput
import encode
import basic_encode

###########################################################################

data = fileinput.ply_file(sys.argv[1])
print "opened %s; got %d points and %d faces" % (sys.argv[1], len(data.points), len(data.faces))

encodings = [
        encode.binary_stl(),
        encode.difference(basic_encode.gammagamma(), mapping.identity()),
        encode.difference(basic_encode.gamma(), mapping.identity()),
        encode.difference(basic_encode.nibble(), mapping.identity()),
        encode.difference(basic_encode.variableword(), mapping.identity()),
        encode.difference(basic_encode.gammagamma(), mapping.morton(data.points)),
]

for encoding in encodings:
    nBytes = 0
    nBytes += encoding.encode_geometry(data.points)
    nBytes += encoding.encode_topology(data.faces)
    print "{}: total of {:,} bytes, {} bytes per vertex".format(str(encoding), nBytes, nBytes / len(data.points))
