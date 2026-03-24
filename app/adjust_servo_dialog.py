from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton


class AdjustServoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adjust Servo")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Servo adjustment controls here."))

        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)

        layout.addWidget(btn_ok)
        self.setLayout(layout)