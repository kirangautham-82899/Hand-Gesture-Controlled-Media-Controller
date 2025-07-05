import cv2
import time
import math
import numpy as np
import pyautogui
import os
import datetime

from hand_detector import HandDetector
from volume_controller import VolumeController
from gesture_utils import is_pinch, is_open_palm

# Initialize
cap = cv2.VideoCapture(0)
detector = HandDetector(detectionCon=0.8)
volCtrl = VolumeController()
pTime = 0
vol = 0
mute_state = False
gesture_text = ""

# Create screenshots folder if not exists
os.makedirs("screenshots", exist_ok=True)

while True:
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img)

    if lmList and len(lmList) >= 10:
        x1, y1 = lmList[4][1:]   # Thumb tip
        x2, y2 = lmList[8][1:]   # Index tip

        # Calculate distance
        length = math.hypot(x2 - x1, y2 - y1)

        # Volume Control (default)
        if not is_pinch(lmList):
            vol_percent = np.interp(length, [20, 180], [0, 100])
            volCtrl.setVolume(vol_percent)
            vol = int(vol_percent)
            gesture_text = "Volume Control"
        else:
            if not mute_state:
                volCtrl.setVolume(0)
                mute_state = True
                gesture_text = "Muted"
            else:
                mute_state = False
                gesture_text = "Unmuted"

        # 📸 Screenshot (tight pinch)
        if is_pinch(lmList, threshold=20):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f'screenshots/screenshot_{timestamp}.png'
            pyautogui.screenshot(filename)
            gesture_text = f"📸 Screenshot saved!"
            time.sleep(0.5)

        # ⏯️ Play/Pause (open palm)
        if is_open_palm(lmList):
            pyautogui.press("space")
            gesture_text = "⏯️ Play/Pause"
            time.sleep(0.5)

        # Volume bar UI
        volBar = np.interp(length, [20, 180], [400, 150])
        cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, f'{vol} %', (40, 450), cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 3)

    # FPS Calculation
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # Display FPS and Gesture
    cv2.putText(img, f'FPS: {int(fps)}', (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    if gesture_text:
        cv2.putText(img, gesture_text, (180, 40),
                    cv2.FONT_HERSHEY_DUPLEX, 1, (255, 0, 255), 2)

    # Show Output
    cv2.imshow("Media Controller", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
