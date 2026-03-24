import cv2
import numpy as np
import math
import os
import sys
import time
from typing import Dict, List, Optional, Tuple

class AnalyzeImage():
    def __init__(self):
        self.size_static = None
        self.draw_cube_size = 30

    def draw_cube_face(self, start_x, start_y, side_data, desc: str) -> None:
        """
        Draw a rubiks cube face on the video
        """
        x = start_x
        y = start_y

        cv2.rectangle(
            self.image,
            (x, y),
            (x + self.draw_cube_size, y + self.draw_cube_size),
            (0, 0, 0),
            -1,
        )

        num_squares = len(list(side_data.keys()))
        size = int(math.sqrt(num_squares))
        gap = 3
        square_width = int((self.draw_cube_size - ((size + 1) * gap)) / size)

        cv2.rectangle(
            self.image,
            (x, y),
            (x + self.draw_cube_size, y + self.draw_cube_size),
            (0, 0, 0),
            -1,
        )
        x += gap
        y += gap

        for (index, square_index) in enumerate(sorted(side_data.keys())):
            (red, green, blue) = side_data[square_index]

            cv2.rectangle(
                (self.image),
                (x, y),
                (x + square_width, y + square_width),
                (blue, green, red),
                -1,
            )

            if (index + 1) % size == 0:
                y += gap + square_width
                x = start_x + gap
            else:
                x += square_width + gap

    def analyze_image_colors(self, width=352, height=240) -> None:
        self.U_data = {}
        self.L_data = {}
        self.F_data = {}
        self.R_data = {}
        self.B_data = {}
        self.D_data = {}

        if self.name == "F":
            self.F_data = deepcopy(self.data)
            self.name = "R"
            self.index = 3

        elif self.name == "R":
            self.R_data = deepcopy(self.data)
            self.name = "B"
            self.index = 4

        elif self.name == "B":
            self.B_data = deepcopy(self.data)
            self.name = "L"
            self.index = 1

        elif self.name == "L":
            self.L_data = deepcopy(self.data)
            self.name = "U"
            self.index = 0

        elif self.name == "U":
            self.U_data = deepcopy(self.data)
            self.name = "D"
            self.index = 5

        elif self.name == "D":
            self.D_data = deepcopy(self.data)
            self.name = "F"
            self.index = 2

        window_width = width * 2
        window_height = height * 2
        self.draw_cube_face(
            self.draw_cube_size,
            height - (self.draw_cube_size * 3),
            self.U_data,
            "U",
        )
        self.draw_cube_face(
            self.draw_cube_size * 0,
            height - (self.draw_cube_size * 2),
            self.L_data,
            "L",
        )
        self.draw_cube_face(
            self.draw_cube_size * 1,
            height - (self.draw_cube_size * 2),
            self.F_data,
            "F",
        )
        self.draw_cube_face(
            self.draw_cube_size * 2,
            height - (self.draw_cube_size * 2),
            self.R_data,
            "R",
        )
        self.draw_cube_face(
            self.draw_cube_size * 3,
            height - (self.draw_cube_size * 2),
            self.B_data,
            "B",
        )
        self.draw_cube_face(
            self.draw_cube_size, 
            height - self.draw_cube_size, 
            self.D_data, 
            "D"
        )

