#!/usr/bin/env python3

import argparse
import cv2
import time
import os
from moveCube import home,mount,photo,resolve_colors

# Command line args
parser = argparse.ArgumentParser("Rubiks Square Extractor")
parser.add_argument("-d", "--directory", type=str, help="Directory of images to examine")
parser.add_argument("-w", "--webcam", type=int, default=None, help="webcam to use...0, 1, etc")
args = parser.parse_args()

directory = args.directory
cam = cv2.VideoCapture(args.webcam)

for (side_index, side_name) in enumerate(("F", "R", "B", "L", "U", "D", "finish")):
    if (side_name != "finish"):
        croppedfile = directory + "/rubiks-" + side_name + ".png"

        photo(side_name)
        time.sleep(2)
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
