from PySide6.QtWidgets import QMainWindow, QStackedWidget, QMenuBar
from PySide6.QtGui import QAction
from app.mainPage import MainPage
from app.calibrationPage import CalibrationPage
from moveCube import moves, servo, maestro
from app.findColors import FindColors, FindSolution
from moveCube.handles import home, mount, park

class MainWindow(QMainWindow):
    def __init__(self, image_dir):
        super().__init__()
        self.image_dir = image_dir
        self.setWindowTitle("Rubik's cube UI")
        self.setGeometry(100, 100, 800, 800)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_page = MainPage(image_dir)
        self.calibration_page = CalibrationPage()
        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.calibration_page)

        self.menu_bar = self.menuBar()
        self.setup_main_menu()

        self.stack.setCurrentIndex(0)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        self.menu_bar.addAction(exit_action)

    def setup_main_menu(self):
        self.menuBar().clear()

        actions_menu = self.menuBar().addMenu("Moves")

        home_action = QAction("Home", self)
        home_action.triggered.connect(home)
        actions_menu.addAction(home_action)

        mount_action = QAction("Mount", self)
        mount_action.triggered.connect(mount)
        actions_menu.addAction(mount_action)

        park_action = QAction("Park", self)
        park_action.triggered.connect(park)
        actions_menu.addAction(park_action)

        actions_menu = self.menuBar().addMenu("Actions")

        pics_action = QAction("Pictures", self)
        #pics_action.triggered.connect(takePictures)
        actions_menu.addAction(pics_action)

        colors_action = QAction("Get colors", self)
        colors_action.triggered.connect(FindColors)
        actions_menu.addAction(colors_action)

        getSolutionAction = QAction("Get Solution", self)
        getSolutionAction.triggered.connect(FindSolution)
        actions_menu.addAction(getSolutionAction)

        calibration_action = QAction("Calibrate", self)
        calibration_action.triggered.connect(self.show_calibration)
        self.menuBar().addAction(calibration_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        self.menu_bar.addAction(exit_action)

    def setup_calibration_menu(self):
        self.menuBar().clear()

        home_action = QAction("Home", self)
        home_action.triggered.connect(self.show_main)
        self.menuBar().addAction(home_action)

    def show_main(self):
        self.stack.setCurrentIndex(0)
        self.setup_main_menu()

    def show_calibration(self):
        self.stack.setCurrentIndex(1)
        self.setup_calibration_menu()

#    def showSolution(self):
#        result = get_solution()
#        self.main_page.resultSolution.setText(result)

