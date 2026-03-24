from PySide6.QtWidgets import QMainWindow, QStackedWidget
from app import calibrationPage, main_page

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Servo Controller")
        self.setGeometry(100, 100, 800, 600)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.main_page = main_page.MainPage(self)
        self.calibration_page = calibrationPage.CalibrationPage()

        self.stack.addWidget(self.main_page)
        self.stack.addWidget(self.calibration_page)

        self.stack.setCurrentIndex(0)

    def show_main(self):
        self.stack.setCurrentIndex(0)

    def show_calibration(self):
        self.stack.setCurrentIndex(1)