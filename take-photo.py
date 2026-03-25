#!/usr/bin/env python3

import argparse
import cv2
import time
import os
from pathlib import Path
from moveCube.moves import *
from moveCube.handles import *
from rubikscolorresolver.solver import resolve_colors

directory = Path('tmp')
directory.mkdir(parents=True, exist_ok=True)
cam = cv2.VideoCapture(0)

# warm up camera auto-exposure/white balance before first useful frame
warmup_frames = 6
for i in range(warmup_frames):
    ret, _ = cam.read()
    time.sleep(0.1)

for (side_index, side_name) in enumerate(("F", "R", "B", "L", "U", "D", "finish")):
    if side_name != "finish":
        croppedfile = directory / f"rubiks-{side_name}.png"

        photo(side_name)
        time.sleep(2)

        ret, frame = cam.read()
        cropped = frame[5:370, 160:540]
        success = cv2.imwrite(str(croppedfile), cropped)
    else:
        photo(side_name)
        break

cam.release()
