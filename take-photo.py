#!/usr/bin/env python3

import argparse
import cv2
import time
import os
from moveCube import home,mount,photo
from rubikscolorresolver.solver import resolve_colors

directory = '../tmp'
cam = cv2.VideoCapture(2)

for (side_index, side_name) in enumerate(("F", "R", "B", "L", "U", "D", "finish")):
    if (side_name != "finish"):
        croppedfile = directory + "/rubiks-" + side_name + ".png"

        photo(side_name)
        time.sleep(1)
        ret, frame = cam.read()
        if not ret:
            print("failed to grab frame")
            break
        cropped = frame[5:370, 160:540]
        cv2.imwrite(croppedfile, cropped)
    else:
        photo(side_name)
        break

cam.release()
