# standard libraries
import cv2
import json
import time
import os
import sys
import array
import logging

from math import sqrt
from subprocess import Popen
from time import sleep

from rubikscubetracker import RubiksImage, merge_two_dicts
import moveCube.servo as servo
import twophase.solver  as tp

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

with open('config.json', mode='r', encoding='utf-8') as jsonFile:
    config = json.load(jsonFile)

serial = config['serial'][os.name]

rTurn = config['right']['turnId']
rHome = config['right']['90']
rLeft = config['right']['0']
rRight = config['right']['180']
r180 = config['right']['270']
rMove = config['right']['moveId']
rIn = config['right']['in']
rOut = config['right']['out']
rPark = config['right']['park']

lTurn = config['left']['turnId']
lHome = config['left']['180']
lLeft = config['left']['90']
lRight = config['left']['270']
l180 = config['left']['0']
lMove = config['left']['moveId']
lIn = config['left']['in']
lOut = config['left']['out']
lPark = config['left']['park']

uTurn = config['up']['turnId']
uHome = config['up']['90']
uLeft = config['up']['0']
uRight = config['up']['180']
u180 = config['up']['270']
uMove = config['up']['moveId']
uIn = config['up']['in']
uOut = config['up']['out']

dTurn = config['down']['turnId']
dHome = config['down']['180']
dLeft = config['down']['90']
dRight = config['down']['270']
d180 = config['down']['0']
dMove = config['down']['moveId']
dIn = config['down']['in']
dOut = config['down']['out']
dPark = config['down']['park']

delay90 = int(config['delay']['90']) / 1000
delay180 = int(config['delay']['180']) / 1000
delayMove = int(config['delay']['move']) / 1000
delayPhoto = int(config['delay']['photo']) / 1000

# Always start with topside up
up = 'up'

def home ():
    servo.moveServo('all', serial, 8, rIn, lIn, uIn, dIn)
    sleep(delay90)
    servo.moveServo('all', serial, 0, rHome, lHome, uHome, dHome)

def mount ():
    servo.moveServo('single', serial, dMove, dOut)
    sleep(2)
    servo.moveServo('dual', serial, 8, rOut, lOut)
    sleep(2)
    servo.moveServo('single', serial, uMove, uOut)

def park ():
    servo.moveServo('all', serial, 8, rPark, lPark, uIn, dPark)
    sleep(delay90)
    servo.moveServo('all', serial, 0, rHome, lHome, uHome, dHome)

def photo (side: str):
    match side:
        case 'F':
            servo.moveServo('dual', serial, 8, rIn, lIn)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 0, rRight, lLeft)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 8, rOut, lOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 10, uIn, dIn)
        case 'R':
            servo.moveServo('dual', serial, 10, uOut, dOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 8, rIn, lIn)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 2, uRight, dLeft)
        case 'B':
            servo.moveServo('dual', serial, 2, u180, d180)
            sleep(2 * delayPhoto)
            servo.moveServo('dual', serial, 8, rOut, lOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 10, uIn, dIn)
        case 'L':
            servo.moveServo('dual', serial, 10, uOut, dOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 8, rIn, lIn)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 2, uLeft, dRight)
        case 'U':
            servo.moveServo('dual', serial, 2, uHome, dHome)
            sleep(delayPhoto)
           # servo.moveServo('dual', serial, 0, rLeft, lRight)
           # sleep(delayPhoto)
            servo.moveServo('dual', serial, 8, rOut, lOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 10, uIn, dIn)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 0, rHome, lHome)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 2, uLeft, dRight)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 10, uOut, dOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 8, rIn, lIn)
        case 'D':
            servo.moveServo('dual', serial, 8, rOut, lOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 10, uIn, dIn)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 0, r180, l180)
            sleep(2 * delayPhoto)
            servo.moveServo('dual', serial, 10, uOut, dOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 8, rIn, lIn)
        case 'finish':
            servo.moveServo('dual', serial, 8, rOut, lOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 10, uIn, dIn)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 0, rRight, lLeft)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 2, uHome, dHome)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 10, uOut, dOut)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 8, rIn, lIn)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 0, rHome, lHome)
            sleep(delayPhoto)
            servo.moveServo('dual', serial, 8, rOut, lOut)
            up == 'up'

def rotate (action: str):
    side = action[0].upper()
    turn = action[-1]
    
    if side == "F":
        dSide = "U"
    elif side == "B":
        dSide = "D"
    else:
        dSide = side

    match turn:
        case '1':
            dest = globals()[dSide.lower() + 'Right']
            delay = delay90
        case '2':
            dest = globals()[dSide.lower() + '180']
            delay = delay180
        case '3':
            dest = globals()[dSide.lower() + 'Left']
            delay = delay90

    match side:
        case 'R':
            servo.moveServo('single', serial, 0, dest)
            sleep(delay90)
            servo.moveServo('single', serial, 8, rIn)
            sleep(delayMove)
            servo.moveServo('single', serial, 0, rHome)
            sleep(delay90)
            servo.moveServo('single', serial, 8, rOut)
            sleep(delayMove)
        case 'L':
            servo.moveServo('single', serial, 1, dest)
            sleep(delay90)
            servo.moveServo('single', serial, 9, lIn)
            sleep(delayMove)
            servo.moveServo('single', serial, 1, lHome)
            sleep(delay90)
            servo.moveServo('single', serial, 9, lIn)
            sleep(delayMove)
        case 'U':
            if (up == 'up'):
                servo.moveServo('single', serial, 2, dest)
                sleep(delay90)
                servo.moveServo('single', serial, 10, uIn)
                sleep(delayMove)
                servo.moveServo('single', serial, 2, uHome)
                sleep(delay90)
                servo.moveServo('single', serial, 10, uOut)
                sleep(delayMove)
            else:
                """
                Upside is front, so turn it up first
                """
                servo.moveServo('dual', serial, 10, uIn, dIn)
                sleep(delay90)
                servo.moveServo('dual', serial, 0, rRight, lLeft)
                sleep(delay90)
                servo.moveServo('dual', serial, 10, uOut, dOut)
                sleep(delay90)
                servo.moveServo('dual', serial, 8, rIn, lIn)
                sleep(delay90)
                servo.moveServo('dual', serial, 0, rHome, lHome)
                sleep(delay90)
                servo.moveServo('dual', serial, 8, rOut, lOut)
                sleep(delay90)
                up == 'up'
                """
                Turn upside to the correct position
                """
                servo.moveServo('single', serial, 2, dest)
                sleep(delay90)
                servo.moveServo('single', serial, 10, uIn)
                sleep(delayMove)
                servo.moveServo('single', serial, 2, uHome)
                sleep(delay90)
                servo.moveServo('single', serial, 10, uOut)
                sleep(delayMove)
        case 'D':
            if (up == 'up'):
                servo.moveServo('single', serial, 3, dest)
                sleep(delay90)
                servo.moveServo('single', serial, 11, dIn)
                sleep(delayMove)
                servo.moveServo('single', serial, 3, dHome)
                sleep(delay90)
                servo.moveServo('single', serial, 11, dOut)
                sleep(delayMove)
            else:
                """
                Upside is front, so turn it up first
                """
                servo.moveServo('dual', serial, 10, uIn, dIn)
                sleep(delay90)
                servo.moveServo('dual', serial, 0, rRight, lLeft)
                sleep(delay90)
                servo.moveServo('dual', serial, 10, uOut, dOut)
                sleep(delay90)
                servo.moveServo('dual', serial, 8, rIn, lIn)
                sleep(delay90)
                servo.moveServo('dual', serial, 0, rHome, lHome)
                sleep(delay90)
                servo.moveServo('dual', serial, 8, rOut, lOut)
                sleep(delay90)
                up == 'up'
                """
                Turn downside to the correct position
                """
                servo.moveServo('single', serial, 3, dest)
                sleep(delay90)
                servo.moveServo('single', serial, 11, dIn)
                sleep(delayMove)
                servo.moveServo('single', serial, 3, dHome)
                sleep(delay90)
                servo.moveServo('single', serial, 11, dOut)
                sleep(delayMove)
        case 'F':
            
            if (up == 'front'):
                servo.moveServo('single', serial, 2, dest)
                sleep(delay90)
                servo.moveServo('single', serial, 10, uIn)
                sleep(delayMove)
                servo.moveServo('single', serial, 2, uHome)
                sleep(delay90)
                servo.moveServo('single', serial, 10, uOut)
                sleep(delayMove)
            else:
                """
                Frontside is front, so turn it up first
                """
                servo.moveServo('dual', serial, 10, uIn, dIn)
                sleep(delay90)
                servo.moveServo('dual', serial, 0, rRight, lLeft)
                sleep(delay90)
                servo.moveServo('dual', serial, 10, uOut, dOut)
                sleep(delay90)
                servo.moveServo('dual', serial, 8, rIn, lIn)
                sleep(delay90)
                servo.moveServo('dual', serial, 0, rHome, lHome)
                sleep(delay90)
                servo.moveServo('dual', serial, 8, rOut, lOut)
                sleep(delay90)
                up == 'front'
                """
                Turn frontside to the correct position
                """
                servo.moveServo('single', serial, 2, dest)
                sleep(delay90)
                servo.moveServo('single', serial, 10, uIn)
                sleep(delayMove)
                servo.moveServo('single', serial, 2, uHome)
                sleep(delay90)
                servo.moveServo('single', serial, 10, uOut)
                sleep(delayMove)
        case 'B':
            if (up == 'front'):
                servo.moveServo('single', serial, 3, dest)
                sleep(delay90)
                servo.moveServo('single', serial, 11, dIn)
                sleep(delayMove)
                servo.moveServo('single', serial, 3, dHome)
                sleep(delay90)
                servo.moveServo('single', serial, 11, dOut)
                sleep(delayMove)
            else:
                """
                Frontside is front, so turn it up first
                """
                servo.moveServo('dual', serial, 10, uIn, dIn)
                sleep(delay90)
                servo.moveServo('dual', serial, 0, rRight, lLeft)
                sleep(delay90)
                servo.moveServo('dual', serial, 10, uOut, dOut)
                sleep(delay90)
                servo.moveServo('dual', serial, 8, rIn, lIn)
                sleep(delay90)
                servo.moveServo('dual', serial, 0, rHome, lHome)
                sleep(delay90)
                servo.moveServo('dual', serial, 8, rOut, lOut)
                sleep(delay90)
                up == 'front'
                """
                Turn backside to the correct position
                """
                servo.moveServo('single', serial, 3, dest)
                sleep(delay90)
                servo.moveServo('single', serial, 11, dIn)
                sleep(delayMove)
                servo.moveServo('single', serial, 3, dHome)
                sleep(delay90)
                servo.moveServo('single', serial, 11, dOut)
                sleep(delayMove)

def move (pos: str):
    side = pos[0].lower()
    match side:
        case 'r':
            if pos == "rIn" or pos == "rOut":
                dev = rMove
            else:
                dev = rTurn
        case 'l':
            if pos == "lIn" or pos == "lOut":
                dev = lMove
            else:
                dev = lTurn
        case 'u':
            if pos == "uIn" or pos == "uOut":
                dev = uMove
            else:
                dev = uTurn
        case 'd':
            if pos == "dIn" or pos == "dOut":
                dev = dMove
            else:
                dev = dTurn

    servo.moveServo('single', serial, dev, pos)

def takePhoto (dir: str):
    cam = cv2.VideoCapture(2)

    for (side_index, side_name) in enumerate(("F", "R", "B", "L", "U", "D", "finish")):
        if (side_name != "finish"):
            croppedfile = dir + "/rubiks-" + side_name + ".png"

            photo(side_name)
            time.sleep(3)
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

def findColors (folder: str):
    cube_size = 3
    data = {}

    for (side_index, side_name) in enumerate(("U", "L", "F", "R", "B", "D")):
        filename = folder + "/rubiks-" + side_name +".png"

        if os.path.exists(filename):
            rimg = RubiksImage(side_index, side_name, debug="false")
            rimg.analyze_file(filename, cube_size)
            data = merge_two_dicts(data, rimg.data)
        else:
            sys.stderr.write(f"ERROR: {filename} does not exist\n")
            sys.exit(1)

    jsonCube = json.dumps(data, sort_keys=True)

    output = folder + "/colors.json"
    with open(output, 'w') as f:
        json.dump(data, f)

    result = resolve_colors(jsonCube)
    twoPhase = tp.solve(result,10,2)

def resolve_colors(rgb):

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

def main():
    readConfig()
