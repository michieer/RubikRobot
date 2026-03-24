import os
import sys
from PySide6.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QMessageBox, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

from app.cubeDisplay import CubeDisplay
from app.cubeVisualizer import CubeVisualizer
from app.cubeJsonGenerator import generateCubeJson
from app.cubeSolverLoader import loadCubeFromJson

class MainPage(QWidget):
    def __init__(self, imageDir: str):
        super().__init__()
        self.imageDir = imageDir
        self.cubeFile = "cube.json"
        self.setWindowTitle("Main Application Page")

        main_layout = QVBoxLayout()

        # Cube face images
        self.cube_widget = CubeDisplay(imageDir)
        images_layout = QHBoxLayout()

        self.cube_widget = CubeDisplay(imageDir)
        images_left = QLabel("Images")
        images_left.setFixedWidth(300)
        main_layout.addWidget(QLabel("Captured Cube Faces:"))
        images_layout.addWidget(self.cube_widget)

        images_right = QWidget()
        images_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        images_layout.addWidget(images_right)
        main_layout.addLayout(images_layout)

        # Generate json from images
        try:
            #generateCubeJson(self.imageDir, self.cubeFile)
            self.cube_solver = loadCubeFromJson(self.imageDir, self.cubeFile)
        except Exception as e:
            print(f"Failed to scan and solve cube: {e}")
            self.cube_solver = None

        # Cube layout and kociemba code from CubeVisualizer
        self.cube_visualizer = CubeVisualizer(self.imageDir, self.cube_solver)

        cube_layout = QHBoxLayout()
        main_layout.addWidget(QLabel("Detected Cube Layout:"))
        cube_left = QWebEngineView()
        cube_left.setAttribute(Qt.WA_TranslucentBackground, True)
        cube_left.setStyleSheet("background: transparent;")
        cube_left.page().setBackgroundColor(Qt.transparent)
        cube_left.setFixedWidth(440)
        cube_left.setMaximumHeight(335) 
        cube_left.setHtml(self.cube_visualizer.get_cube_layout_html())
        cube_layout.addWidget(cube_left)
        cube_right = QWidget()
        cube_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        cube_layout.addWidget(cube_right)
        main_layout.addLayout(cube_layout)

        solution_layout = QHBoxLayout()
        solution_left = QLabel("Solution")
        solution_left.setStyleSheet("background: transparent; border: none;")
        solution_left.setFrameShape(QLabel.NoFrame)
        solution_left.setAttribute(Qt.WA_TranslucentBackground, True)
        solution_left.setAutoFillBackground(False)
        solution_left.setFixedWidth(200)
        main_layout.addWidget(QLabel("Kociemba Code:"))
        solution_layout.addWidget(self.cube_visualizer.kociemba_display)
        solution_right = QWidget()
        solution_right.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        solution_layout.addWidget(solution_right)

        main_layout.addLayout(solution_layout)
        self.setLayout(main_layout)
    
    def scan_and_update(self):
        try:
            generateCubeJson(self.imageDir, self.cubeFile)
            jsonPath = os.path
            self.cube_solver = loadCubeFromJson(self.imageDir, self.cubeFile)
            self.visualizer.cube_solver = self.cube_solver
            self.visualizer.update_cube_data()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to scan and solve cube:\n{str(e)}")

# Entry point
if __name__ == "__main__":
    app = QApplication(sys.argv)

    main_page = MainPage(imageDir="tmp")
    main_page.resize(800, 600)
    main_page.show()

    sys.exit(app.exec_())