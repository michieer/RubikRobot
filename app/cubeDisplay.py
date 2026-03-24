from PySide6.QtWidgets import QWidget, QLabel, QGridLayout, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os

class CubeDisplay(QWidget):
    def __init__(self, image_dir="tmp"):
        super().__init__()
        layout = QGridLayout()

        faces = ['U', 'D', 'L', 'R', 'F', 'B']
        images = {face: os.path.join(image_dir, f"rubik-{face}.png") for face in faces}

        positions = {
            'U': (0, 1),
            'L': (1, 0),
            'F': (1, 1),
            'R': (1, 2),
            'B': (1, 3),
            'D': (2, 1)
        }

        fixed_size = 100

        for face, path in images.items():
            label = QLabel()
            pixmap = QPixmap(path).scaled(
                fixed_size,
                fixed_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            label.setPixmap(pixmap)
            label.setFixedSize(fixed_size, fixed_size)
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            layout.addWidget(label, *positions[face])

        layout.setSpacing(2)
        self.setLayout(layout)