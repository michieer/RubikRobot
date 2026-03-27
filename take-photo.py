#!/usr/bin/env python3

import argparse
import cv2
import time
import os
import json
from pathlib import Path
from moveCube.moves import *
from moveCube.handles import *
from analyzeCube.cubeTracker import extract_colors_from_image
from analyzeCube.colorresolver.solver import resolve_colors

camera = 1
directory = Path('tmp')
directory.mkdir(parents=True, exist_ok=True)
cam = cv2.VideoCapture(camera)

# warm up camera auto-exposure/white balance before first useful frame
warmup_frames = 6
for i in range(warmup_frames):
    ret, _ = cam.read()
    time.sleep(0.1)

list_colors = []
for (side_index, side_name) in enumerate(("F", "R", "B", "L", "U", "D", "finish")):
    if side_name != "finish":
        croppedfile = directory / f"rubiks-{side_name}.png"
        #fullfile = directory / f"rubiks-{side_name}-full.png"

        photo(side_name)
        time.sleep(2)

        ret, frame = cam.read()
        cropped = frame[10:390, 140:520]
        #cropped = frame[23:345, 168:507]

        cv2.imwrite(str(croppedfile), cropped)
        #cv2.imwrite(str(fullfile), frame)
        
        # Extract colors from the saved image
        colors = extract_colors_from_image(str(croppedfile))
        list_colors.append(colors)
    else:
        photo(side_name)
        break

cam.release()

# Reorder to standard cube order: U, L, F, R, B, D
reordered_faces = [list_colors[4], list_colors[3], list_colors[0], list_colors[1], list_colors[2], list_colors[5]]

# Flatten into a single dict with square indices (1-54 for 3x3x3)
data = {}
square_index = 1
for face in reordered_faces:
    for rgb in face:
        data[square_index] = rgb
        square_index += 1

# Save raw RGB JSON (optional, for debugging)
raw_output_path = directory / "raw_colors.json"
with open(raw_output_path, 'w') as f:
    json.dump(data, f, indent=4, sort_keys=True)

# Resolve colors to cube notation and save resolved JSON
json_str = json.dumps(data, sort_keys=True)
resolved_json_str = resolve_colors(rgb=json_str, use_json=True)
resolved_data = json.loads(resolved_json_str)
kociemba_string = resolved_data['kociemba']

print(f"Kociemba string: {kociemba_string}")
twoPhase = tp.solve(kociemba_string, 10, 2)
print(f"Solution: {twoPhase}")
