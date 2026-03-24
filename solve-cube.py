#!/usr/bin/env python3

import os
import sys
from moveCube import *

folder = sys.argv[1]

solution = os.path.join(folder, f"solution")
with open(solution, 'r') as f:
    solution = f.read()

for (move_index, move) in enumerate(solution.split(' ')):
    rotate(move)
    sleep(2)