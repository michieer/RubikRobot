#!/usr/bin/env python3

# Result of the cube is givan as:
# UBFLUUDRBLBLFRDUFBFBDLFRRLLFUFRDUBRRBBRFLFLDUDDRLBDDUU
#
# Moves to solve the cube given as:
# L3 U1 B1 R2 F3 L1 F3 U2 L1 U3 B3 U2 B1 L2 F1 U2 R2 L2 B2
# Here, U, R, F, D, L and B denote the Up, Right, Front, Down, Left and Back faces of the cube. 
# 1, 2, and 3 denote a 90°, 180° and 270° clockwise rotation of the corresponding face. 

import json
import time
import os
import sys
import twophase.solver  as tp
from moveCube import resolve_colors
from rubikscubetracker import RubiksImage, merge_two_dicts

cube_size = 3
data = {}
folder = sys.argv[1]

for (side_index, side_name) in enumerate(("U", "L", "F", "R", "B", "D")):
    filename = os.path.join(folder, f"rubiks-{side_name}.png")

    if os.path.exists(filename):
        rimg = RubiksImage(side_index, side_name, debug=False)
        rimg.analyze_file(filename, cube_size)
        data = merge_two_dicts(data, rimg.data)
    else:
        sys.stderr.write(f"ERROR: {filename} does not exist\n")
        sys.exit(1)

jsonColors = json.dumps(data, sort_keys=True)

output = os.path.join(folder, f"colors.json")
with open(output, 'w') as f:
    json.dump(data, f)

result = resolve_colors(jsonColors)
print("\nInputstring: " + result + "\n")

twoPhase = tp.solve(result,10,2)
print("TwoPhase solution: " + twoPhase + "\n")
