from PySide6 import QtGui
from PySide6.QtWidgets import QWidget, QTextEdit, QLabel
from PySide6.QtCore import Qt
import os

class CubeVisualizer(QWidget):
    def __init__(self, image_dir: str, cube_solver=None):
        super().__init__()
        self.image_dir = image_dir
        self.cube_solver = cube_solver
        if self.cube_solver is not None:
            self.sideU = self.cube_solver.sideU
            self.sideR = self.cube_solver.sideR
            self.sideF = self.cube_solver.sideF
            self.sideD = self.cube_solver.sideD
            self.sideL = self.cube_solver.sideL
            self.sideB = self.cube_solver.sideB

        # These widgets will be accessed from MainPage
        self.layout_display = QTextEdit()
        self.layout_display.setReadOnly(True)
        self.layout_display.setWordWrapMode(QtGui.QTextOption.NoWrap)
        self.layout_display.setFixedWidth(400)
        self.layout_display.setMinimumHeight(300)
        self.layout_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.layout_display.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.kociemba_display = QLabel()
        self.kociemba_display.setStyleSheet("font-weight: bold; font-size: 14px;")

        self.update_cube_data()

    def update_cube_data(self):
        layout_text = self.get_cube_layout_html()
        output_path = os.path.join("tmp/layout.html")
        with open(output_path, 'w') as f:
            f.write(layout_text)

        kociemba_data = self.cube_for_kociemba_strict()
        kociemba_code = "".join(kociemba_data)

        self.layout_display.setHtml(layout_text)
        self.kociemba_display.setText(kociemba_code)

    def cube_for_kociemba_strict(self):
        data = []
        for side in (self.sideU, self.sideR, self.sideF, self.sideD, self.sideL, self.sideB):
            for x in range(side.min_pos, side.max_pos + 1):
                square = side.squares[x]
                data.append(square.side_name)
                print(str(side) + "," + str(x) + "," + str(side.squares[x]))
        return data

    def get_cube_layout_html(self) -> str:
        self.sides = {
            "U": self.sideU,
            "R": self.sideR,
            "F": self.sideF,
            "D": self.sideD,
            "L": self.sideL,
            "B": self.sideB,
        }

        color_map_html = {
            "OR": "#FFA500",  # Orange
            "Rd": "#FF0000",  # Red
            "Gr": "#00FF00",  # Green
            "Ye": "#FFFF00",  # Yellow
            "Bu": "#0000FF",  # Blue
            "Wh": "#FFFFFF",  # White
        }

        width = 3

        html_lines = []

        # Outer table: big layout
        html_lines.append(
            "<table "
            "style='border-collapse: separate; border-spacing: 1px 1px; "
            "font-family: Courier New, monospace; font-size: 24px; "
            "color: white; text-align:center;'"
            " cellpadding='0' cellspacing='0'>"
        )

        # Helper to build a 3x3 face table for Qt-friendly spacing
        def build_face_table(side):
            face_html = ["<table cellpadding='2' cellspacing='2' style='margin:auto;'>"]
            for row in range(width):
                face_html.append("<tr>")
                for col in range(width):
                    idx = side.min_pos + row * width + col
                    square = side.squares[idx]
                    color_name = square.color_name
                    color = color_map_html.get(color_name, "#FFFFFF")

                    # Each square as a small cell with background color, color text centered
                    face_html.append(
                        f"<td style='width: 32px; height: 32px; "
                        f"background-color: black; color: {color}; "
                        f"padding: 0; margin: 0; text-align:center; vertical-align:middle;"
                        #f"font-size: 16px;'>{color_name}</td>"
                        f"font-size: 16px;'>{color_name}</td>"
                    )
                face_html.append("</tr>")
            face_html.append("</table>")
            return "".join(face_html)

        # --- TOP row ---
        html_lines.append("<tr>")
        html_lines.append("<td></td>")  # indent left
        html_lines.append(f"<td style='background-color: black; '>{build_face_table(self.sides['U'])}</td>")
        html_lines.extend(["<td></td>"] * 3)  # indent right
        html_lines.append("</tr>")

        # --- MIDDLE row ---
        html_lines.append("<tr>")
        for side_name in ["L", "F", "R", "B"]:
            html_lines.append(f"<td style='background-color: black; '>{build_face_table(self.sides[side_name])}</td>")
        html_lines.append("</tr>")

        # --- BOTTOM row ---
        html_lines.append("<tr>")
        html_lines.append("<td></td>")  # indent left
        html_lines.append(f"<td style='background-color: black; '>{build_face_table(self.sides['D'])}</td>")
        html_lines.extend(["<td></td>"] * 3)  # indent right
        html_lines.append("</tr>")

        html_lines.append("</table>")

        return "\n".join(html_lines)
