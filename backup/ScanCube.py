#!/usr/bin/env python3

import argparse
import cv2
import time
import os
import sys
import json
from moveCube import home,mount,photo,resolve_colors
from rubikscubetracker import RubiksImage, merge_two_dicts

global colors

parser = argparse.ArgumentParser("Rubiks Square Extractor")
parser.add_argument("-d", "--directory", type=str, help="Directory of images to examine")
parser.add_argument("-w", "--webcam", type=int, default=None, help="webcam to use...0, 1, etc")
args = parser.parse_args()

directory = args.directory
cam = cv2.VideoCapture(args.webcam)
cube_size = 3
data = {}
list = []

for (side_index, side_name) in enumerate(("F", "R", "B", "L", "U", "D", "finish")):
    if (side_name != "finish"):
        photo(side_name)
        time.sleep(2)
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cropped = frame[5:370, 160:540]
        filename = directory + "/rubiks-" + side_name + ".png"
        cv2.imwrite(filename, cropped)

        rimg = RubiksImage(side_index, side_name, debug=False)
        rimg.analyze_file(filename, cube_size)
        list.append(rimg.data)
    else:
        photo(side_name)
        break

cam.release()

# Reorder list
dict = {}
dict.update(list[4])
dict.update(list[3])
dict.update(list[0])
dict.update(list[1])
dict.update(list[2])
dict.update(list[5])

data = {}
i = 1
for x,key in enumerate(dict.values()):
    data[i] = key
    i+= 1

jsonColors = json.dumps(data, sort_keys=True)
colors = resolve_colors(jsonColors)

# Save json result
output = os.path.join(directory, f"colors.json")
with open(output, 'w') as f:
    json.dump(data, f)

print(colors)
