import os
import json
from rubikscolorresolver.solver import RubiksColorSolverGeneric

def loadCubeFromJson(imageDir: str, cubeFile: str) -> RubiksColorSolverGeneric:
    json_path = os.path.join(imageDir, cubeFile)
    with open(json_path, "r") as f:
        scan_data = json.load(f)

    scan_data = {int(key): tuple(value) for key, value in scan_data.items()}
    square_count = len(scan_data)
    square_count_per_side = square_count // 6
    width = int(square_count_per_side ** 0.5)

    if width != 3:
        raise ValueError(f"Expected a 3x3 cube, but got width {width}. Total squares: {square_count}")

    cube = RubiksColorSolverGeneric(width)
    cube.write_debug_file = False
    cube.enter_scan_data(scan_data)
    cube.crunch_colors()

    return cube