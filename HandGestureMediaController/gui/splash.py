from PyQt6.QtWidgets import QLabel, QWidget, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QPropertyAnimation, pyqtSignal, QTimer
from PyQt6.QtGui import QFont

class SplashScreen(QWidget):
    splash_done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome")
        self.setFixedSize(800, 500)
        self.setStyleSheet("background-color: black;")
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.label = QLabel("🎬 Opening Hand Gesture Controller\n")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color: white; font-size: 24px;")
        self.label.setFont(QFont("Arial", 22, QFont.Weight.Bold))

        opacity_effect = QGraphicsOpacityEffect()
        self.label.setGraphicsEffect(opacity_effect)

        self.animation = QPropertyAnimation(opacity_effect, b"opacity")
        self.animation.setDuration(2500)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)

        layout.addWidget(self.label)

       
        QTimer.singleShot(3500, self.finish_splash)

        self.animation.start()

    def finish_splash(self):
        self.close()
        self.splash_done.emit()
