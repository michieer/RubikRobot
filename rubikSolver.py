import sys
from PySide6.QtWidgets import QApplication
from app.mainWindow import MainWindow

def main():
    app = QApplication(sys.argv)
    image_dir = 'tmp'
    window = MainWindow(image_dir)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()