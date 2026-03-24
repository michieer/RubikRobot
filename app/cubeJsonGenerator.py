import os
import json
from rubikscubetracker import RubiksImage, merge_two_dicts

def generateCubeJson(imageDir: str, outputFile: str, debug=False):
    cube_size = 3
    data = {}

    face_order = ["U", "L", "F", "R", "B", "D"]

    for side_index, side_name in enumerate(face_order):
        filename = os.path.join(imageDir, f"rubik-{side_name}.png")

        if os.path.exists(filename):
            rimg = RubiksImage(side_index, side_name, debug=debug)
            success = rimg.analyze_file(filename, cube_size)

            if not success:
                raise RuntimeError(f"Failed to analyze {filename}")

            # Guess cube size from side if needed
            if cube_size is None:
                side_square_count = len(rimg.data)
                cube_size = int(sqrt(side_square_count))

            data = merge_two_dicts(data, rimg.data)

        else:
            raise FileNotFoundError(f"ERROR: {filename} does not exist")

    # Save the combined cube data as JSON
    output_path = os.path.join(imageDir, outputFile)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4, sort_keys=True)

    print(f"Cube JSON saved to {output_path}")