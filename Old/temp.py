from PySide6.QtWidgets import (
    QWidget, QLabel, QTextEdit, QLineEdit, QVBoxLayout, QHBoxLayout, QScrollArea
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os


class CubeVisualizer(QWidget):
    def __init__(self, image_dir: str, cube_solver):
        super().__init__()
        self.image_dir = image_dir
        self.cube_solver = cube_solver  # Instance of RubiksColorSolverGeneric

        self.init_ui()

    def init_ui(self):
        # Image display area
        self.image_area = QScrollArea()
        self.image_container = QWidget()
        self.image_layout = QHBoxLayout()
        self.image_container.setLayout(self.image_layout)
        self.image_area.setWidget(self.image_container)
        self.image_area.setWidgetResizable(True)

        # Load images
        self.load_images()

        # Cube layout display
        self.layout_display = QTextEdit()
        self.layout_display.setReadOnly(True)
        self.layout_display.setStyleSheet("font-family: monospace; font-size: 12px;")

        # Kociemba code display
        self.kociemba_display = QLineEdit()
        self.kociemba_display.setReadOnly(True)
        self.kociemba_display.setStyleSheet("font-weight: bold; font-size: 14px;")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(QLabel("Captured Cube Faces:"))
        main_layout.addWidget(self.image_area)
        main_layout.addWidget(QLabel("Detected Cube Layout:"))
        main_layout.addWidget(self.layout_display)
        main_layout.addWidget(QLabel("Kociemba Code:"))
        main_layout.addWidget(self.kociemba_display)

        self.setLayout(main_layout)

        # Populate cube data
        self.update_cube_data()

    def load_images(self):
        if not os.path.isdir(self.image_dir):
            return

        for filename in sorted(os.listdir(self.image_dir)):
            if filename.lower().endswith((".png", ".jpg", ".jpeg")):
                path = os.path.join(self.image_dir, filename)
                label = QLabel()
                pixmap = QPixmap(path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(pixmap)
                self.image_layout.addWidget(label)

    def update_cube_data(self):
        layout_text = self.cube_solver.get_cube_layout_plain()
        kociemba_code = self.cube_solver.get_kociemba_code()

        self.layout_display.setPlainText(layout_text)
        self.kociemba_display.setText(kociemba_code)
