from PySide6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QComboBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class CalibrationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFixedSize(1280, 800)

        # Load and display image
        image = QLabel(self)
        pixmap = QPixmap("Otvinta-rubik.png")
        image.setPixmap(pixmap)
        image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image.resize(500, 500)
        image.move(300, 150)  # Center-ish position

        # Common position labels
        positions = ["Left", "Home", "Right", "180", "Move", "In", "Out", "Park"]
        positions_per_side = {
            "top": (positions, 400, 50),
            "left": (positions, 50, 300),
            "right": (positions, 750, 300),
            "bottom": (positions, 500, 500)
        }

        self.fields = {}

        for side, (pos_list, x_base, y_base) in positions_per_side.items():
            for i, pos in enumerate(pos_list):
                x = x_base
                y = y_base + i * 30

                # Label
                label = QLabel(pos, self)
                label.move(x, y)

                # Input
                input_field = QLineEdit(self)
                input_field.setFixedWidth(40)
                input_field.move(x + 50, y)

                # ComboBox (just for example)
                combo = QComboBox(self)
                combo.addItems(["size='4'", "size='5'", "size='6'"])
                combo.setFixedWidth(70)
                combo.move(x + 100, y)

                # Go button
                go_button = QPushButton("Go", self)
                go_button.setFixedWidth(40)
                go_button.move(x + 180, y)

                # Calibrate button
                cal_button = QPushButton("Calibrate", self)
                cal_button.setFixedWidth(80)
                cal_button.move(x + 225, y)

                self.fields[f"{side}_{pos}"] = {
                    "input": input_field,
                    "combo": combo,
                    "go": go_button,
                    "calibrate": cal_button,
                }

        # Optional: Delay section
        delay_label = QLabel("Delay", self)
        delay_label.move(50, 520)
        delay_input = QLineEdit(self)
        delay_input.move(100, 520)

        # Submit Button
        submit_button = QPushButton("Submit", self)
        submit_button.move(50, 560)

        main_button = QPushButton("Back to MainPage", self)
        main_button.move(700, 560)

        # When button clicked, call method to switch page
        main_button.clicked.connect(self.goto_main)

    def goto_main(self):
        main_window = self.window()
        if hasattr(main_window, 'show_main'):
            main_window.show_main()