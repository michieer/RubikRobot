import os
import sys
import json
from math import sqrt
from rubikscubetracker import RubiksImage, merge_two_dicts

def analyze_directory(directory_path, json_file, debug=False):
    if not os.path.isdir(directory_path):
        raise FileNotFoundError(f"Directory '{directory_path}' does not exist")

    data = {}
    cube_size = None

    for side_index, side_name in enumerate(("U", "L", "F", "R", "B", "D")):
        filename = os.path.join(directory_path, f"rubik-{side_name}.png")

        if not os.path.exists(filename):
            raise FileNotFoundError(f"Missing required image: {filename}")

        rimg = RubiksImage(side_index, side_name, debug=debug)
        rimg.analyze_file(filename, cube_size)

        if cube_size is None:
            side_square_count = len(list(rimg.data.keys()))
            cube_size = int(sqrt(side_square_count))

        data = merge_two_dicts(data, rimg.data)

    print((json.dumps(data, sort_keys=True)))
    output = os.path.join(directory_path, json_file)
    with open(output, 'w') as f:
        json.dump(data, f)
