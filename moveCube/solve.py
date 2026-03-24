# standard libraries
import cv2
import json
import time
import os
import sys
import array
import logging
import numpy as np
import twophase.solver  as tp

from moveCube.handles import *
from moveCube.moves import *
from math import sqrt
from subprocess import Popen
from time import sleep

from rubikscubetracker import RubiksImage

try:
    # standard libraries
    from typing import Dict, List, Tuple, Union
except ImportError:
    # this will barf for micropython...ignore it
    pass

# rubiks cube libraries
from rubikscolorresolver.solver import RubiksColorSolverGeneric
from rubikscolorresolver.color import LabColor, html_color, lab_distance, rgb2lab
from rubikscolorresolver.cube import RubiksCube
from rubikscolorresolver.permutations import (
    even_cube_center_color_permutations,
    len_even_cube_center_color_permutations,
    odd_cube_center_color_permutations,
)
from rubikscolorresolver.square import Square
from rubikscolorresolver.tsp_solver_greedy import solve_tsp
from rubikscolorresolver.www import HTML_FILENAME, WwwMixin, crayola_colors, open_mode

def ScanCube (webcam: int, directory: str):
    cam = cv2.VideoCapture(webcam)
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
            framefile = directory + "/rubiks-" + side_name + "-full.png"
            cv2.imwrite(framefile, frame)

            rimg = RubiksImage(side_index, side_name, debug=False)
            rimg.analyze_image(frame)

            list.append(rimg.data)
        else:
            photo(side_name)
            break

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
        i += 1

    # Get matching colors
    jsonColors = json.dumps(data, sort_keys=True)
    colors = ResolveColors(jsonColors)

    # Save json result
    output = os.path.join(directory, f"colors.json")
    with open(output, 'w') as f:
        json.dump(data, f)

    return colors

def SolveCube (colors: str):
    twoPhase = (tp.solve(colors,10,2))
    list = (twoPhase.split(' '))[:-1]
    steps = len(list)
    print("TwoPhase solution: " + twoPhase + " (" + str(steps) + " moves)\n")
    
    # Sent moves to robot
    front = "front"
    for i in range(0,steps):
        Finished = False
        move = list[i]
        print("Move " + str(i + 1) + ": " + move + "\n")

        side = move[0].upper()
        if ((front == "front") and ((side == "F") or (side == "B"))):
            front = "right"
            turn = "right"
        elif ((front == "right") and ((side == "R") or (side == "L"))):
            front = "front"
            turn = "front"
        else:
            turn = "none"

        rotate(list[i], turn)

        while True:
            if (Finished == True):
                break

    park()

def ResolveColors(rgb):

    scan_data = eval(rgb)

    for key, value in scan_data.items():
        scan_data[key] = tuple(value)

    square_count = len(list(scan_data.keys()))
    square_count_per_side = int(square_count / 6)
    width = int(sqrt(square_count_per_side))

    cube = RubiksColorSolverGeneric(width)
    cube.write_debug_file = True
    cube.enter_scan_data(scan_data)
    cube.crunch_colors()
    cube.print_profile_data()
    cube.print_cube()

    result = "".join(cube.cube_for_kociemba_strict())

    return result

