#!/usr/bin/env python3

import argparse
import sys
import twophase.solver  as tp
from moveCube import *

parser = argparse.ArgumentParser("Rubiks Square Extractor")
parser.add_argument("-c", "--colors", type=str, help="List of cubecolors")
args = parser.parse_args()

colors = args.colors

twoPhase = (tp.solve(colors,10,2))
print("TwoPhase solution: " + twoPhase + "\n")

# Set front to "front"
front = 'front'

i = 1
# Sent moves to robot
for (move_index, move) in enumerate(twoPhase.split(' ')):
    print("Move " + i + ": " + move + "\n")
    rotate(move)
    i += 1
    
    while True:
        input("Press Enter to continue...")
        break
