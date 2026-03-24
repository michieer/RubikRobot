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
from app.mainPage import MainPage
from moveCube import resolve_colors
from rubikscubetracker import RubiksImage, merge_two_dicts
from rubikscolorresolver.solver import RubiksColorSolverGeneric

def FindColors ():
    main_page = MainPage()
    folder = 'tmp'

    json_path = os.path.join(folder, f"colors.json")
    with open(json_path, "r") as f:
        scan_data = json.load(f)

    # Convert values to tuples
    for key, value in scan_data.items():
        scan_data[int(key)] = tuple(value)

    square_count = len(scan_data)
    square_count_per_side = square_count // 6
    width = int(square_count_per_side ** 0.5)

    cube = RubiksColorSolverGeneric(width)
    cube.write_debug_file = False  # Set to True if you want HTML output
    cube.enter_scan_data(scan_data)
    cube.crunch_colors()

    return cube

def FindSolution (result):
    main_page = MainPage()
    folder = 'tmp'

    twoPhase = (tp.solve(result,10,2)).strip()
    steps = len(twoPhase.split(' '))

    result = "TwoPhase solution: " + twoPhase + " (" + str(steps) + " moves)"
    main_page.resultSolution.setText(result)

def load_cube_from_json(json_path: str) -> RubiksColorSolverGeneric:
    with open(json_path, "r") as f:
        scan_data = json.load(f)

    # Convert values to tuples
    for key, value in scan_data.items():
        scan_data[int(key)] = tuple(value)

    square_count = len(scan_data)
    square_count_per_side = square_count // 6
    width = int(square_count_per_side ** 0.5)

    cube = RubiksColorSolverGeneric(width)
    cube.write_debug_file = False  # Set to True if you want HTML output
    cube.enter_scan_data(scan_data)
    cube.crunch_colors()

    return cube
