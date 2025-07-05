import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import cv2
import time
import datetime
import numpy as np
import pyautogui
from splash import SplashScreen

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QFont
from PyQt6.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QGraphicsDropShadowEffect
)

from hand_detector import HandDetector
from volume_controller import VolumeController
from gesture_utils import is_pinch, is_open_palm


class GestureControllerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("🖐️ Hand Gesture Media Controller")
        self.setStyleSheet("background-color: white;")
        self.setFixedSize(960, 720)

        # Shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(30)
        self.shadow.setOffset(0, 0)
        self.shadow.setColor(Qt.GlobalColor.black)

        # Title Label
        self.titleLabel = QLabel("🎮 Gesture Media Controller")
        self.titleLabel.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.titleLabel.setStyleSheet("color: #2c3e50;")
        self.titleLabel.setGraphicsEffect(self.shadow)
        self.titleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Video Feed Label
        self.videoLabel = QLabel()
        self.videoLabel.setFixedSize(900, 500)
        self.videoLabel.setStyleSheet("border: 4px solid #2c3e50; border-radius: 15px;")
        self.videoLabel.setGraphicsEffect(self.shadow)

        # Gesture Info Label
        self.infoLabel = QLabel("")
        self.infoLabel.setFont(QFont("Arial", 16))
        self.infoLabel.setStyleSheet("color: #8e44ad;")
        self.infoLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Buttons
        self.startBtn = QPushButton("▶ Start Controller")
        self.stopBtn = QPushButton("⛔ Stop Controller")

        for btn in [self.startBtn, self.stopBtn]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: black;
                    color: white;
                    border-radius: 20px;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #2c3e50;
                }
            """)

        self.startBtn.clicked.connect(self.start_controller)
        self.stopBtn.clicked.connect(self.stop_controller)

        # Layouts
        btnLayout = QHBoxLayout()
        btnLayout.addWidget(self.startBtn)
        btnLayout.addWidget(self.stopBtn)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.titleLabel)
        mainLayout.addWidget(self.videoLabel)
        mainLayout.addWidget(self.infoLabel)
        mainLayout.addLayout(btnLayout)

        self.setLayout(mainLayout)

        # Timer for webcam
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Gesture controller setup
        self.cap = None
        self.detector = HandDetector(detectionCon=0.8)
        self.volCtrl = VolumeController()
        self.pTime = 0
        self.mute_state = False
        os.makedirs("screenshots", exist_ok=True)

    def start_controller(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)

    def stop_controller(self):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        self.videoLabel.clear()
        self.infoLabel.setText("")

    def update_frame(self):
        success, img = self.cap.read()
        if not success:
            return

        img = cv2.flip(img, 1)
        img = self.detector.findHands(img)
        lmList = self.detector.findPosition(img)

        gesture_text = ""
        vol = 0

        if lmList and len(lmList) >= 10:
            x1, y1 = lmList[4][1:]
            x2, y2 = lmList[8][1:]
            length = np.hypot(x2 - x1, y2 - y1)

            if not is_pinch(lmList):
                vol_percent = np.interp(length, [20, 180], [0, 100])
                self.volCtrl.setVolume(vol_percent)
                vol = int(vol_percent)
                gesture_text = f"🔊 Volume: {vol}%"
            else:
                if not self.mute_state:
                    self.volCtrl.setVolume(0)
                    self.mute_state = True
                    gesture_text = "🔇 Muted"
                else:
                    self.mute_state = False
                    gesture_text = "🔈 Unmuted"

            if is_pinch(lmList, threshold=20):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f'screenshots/screenshot_{timestamp}.png'
                pyautogui.screenshot(filename)
                gesture_text = "📸 Screenshot Taken"
                time.sleep(0.5)

            if is_open_palm(lmList):
                pyautogui.press("space")
                gesture_text = "⏯️ Play/Pause"
                time.sleep(0.5)

        # FPS
        cTime = time.time()
        fps = 1 / (cTime - self.pTime)
        self.pTime = cTime
        gesture_text += f" | FPS: {int(fps)}"

        self.infoLabel.setText(gesture_text)

        # Convert to QImage for GUI
        rgbImage = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgbImage.shape
        bytesPerLine = ch * w
        qtImage = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format.Format_RGB888)
        self.videoLabel.setPixmap(QPixmap.fromImage(qtImage))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    splash = SplashScreen()
    window = GestureControllerApp()

    # When splash is done, show main app
    splash.splash_done.connect(window.show)

    splash.show()
    sys.exit(app.exec())
