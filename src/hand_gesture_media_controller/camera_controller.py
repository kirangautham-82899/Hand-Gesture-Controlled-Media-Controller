import datetime
import os
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui

from .core.gesture_utils import is_fist, is_open_palm, is_pinch, is_rock_sign, is_v_sign
from .core.hand_detector import HandDetector
from .core.volume_controller import VolumeController


def save_screenshot(path):
    def worker():
        pyautogui.screenshot(str(path))

    threading.Thread(target=worker, daemon=True).start()


def press_action_key(preferred_key, fallback_key=None):
    try:
        pyautogui.press(preferred_key)
    except Exception:
        if fallback_key:
            pyautogui.press(fallback_key)


def main():
    cap_backend = cv2.CAP_DSHOW if os.name == "nt" else 0
    cap = cv2.VideoCapture(0, cap_backend)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    cap.set(cv2.CAP_PROP_FPS, 60)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    detector = HandDetector(maxHands=1, detectionCon=0.75, trackCon=0.7, modelComplexity=0)
    vol_ctrl = VolumeController()

    project_root = Path(__file__).resolve().parents[2]
    screenshot_dir = project_root / "screenshots"
    screenshot_dir.mkdir(exist_ok=True)

    process_scale = 0.72
    last_frame = time.monotonic()
    smoothed_fps = 0.0

    last_volume = 0
    last_nonzero_volume = 40
    last_volume_commit = 0.0
    last_screenshot_time = 0.0
    last_media_toggle_time = 0.0
    last_mute_toggle_time = 0.0
    last_next_track_time = 0.0
    last_prev_track_time = 0.0
    last_fullscreen_time = 0.0
    pinch_active = False
    muted = False

    while True:
        ok, frame = cap.read()
        if not ok:
            continue

        frame = cv2.flip(frame, 1)
        small = cv2.resize(frame, None, fx=process_scale, fy=process_scale, interpolation=cv2.INTER_LINEAR)
        detector.findHands(small, draw=False)
        lm_small = detector.findPosition(small)

        action = "Hand not detected"
        now = time.monotonic()

        if lm_small and len(lm_small) >= 9:
            scale_x = frame.shape[1] / small.shape[1]
            scale_y = frame.shape[0] / small.shape[0]
            lm = [(idx, int(x * scale_x), int(y * scale_y)) for idx, x, y in lm_small]

            pinch = is_pinch(lm, threshold=44)
            tight_pinch = is_pinch(lm, threshold=24)
            open_palm = is_open_palm(lm)
            v_sign = is_v_sign(lm)
            rock_sign = is_rock_sign(lm)
            fist = is_fist(lm)

            x1, y1 = lm[4][1:]
            x2, y2 = lm[8][1:]
            dist = np.hypot(x2 - x1, y2 - y1)

            if tight_pinch and (now - last_screenshot_time) > 1.2:
                filename = screenshot_dir / f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                save_screenshot(filename)
                last_screenshot_time = now
                action = "Screenshot saved"
            elif pinch and not pinch_active and (now - last_mute_toggle_time) > 0.75:
                if muted:
                    vol_ctrl.setVolume(last_nonzero_volume)
                    last_volume = last_nonzero_volume
                    muted = False
                    action = "Unmuted"
                else:
                    vol_ctrl.setVolume(0)
                    last_volume = 0
                    muted = True
                    action = "Muted"
                last_mute_toggle_time = now
            elif open_palm and (now - last_media_toggle_time) > 0.9:
                press_action_key("playpause", "space")
                last_media_toggle_time = now
                action = "Play/Pause"
            elif open_palm:
                action = "Open Palm"
            elif v_sign and (now - last_next_track_time) > 0.9:
                press_action_key("nexttrack", "right")
                last_next_track_time = now
                action = "Next Track"
            elif v_sign:
                action = "V Sign"
            elif rock_sign and (now - last_prev_track_time) > 0.9:
                press_action_key("prevtrack", "left")
                last_prev_track_time = now
                action = "Previous Track"
            elif rock_sign:
                action = "Rock Sign"
            elif fist and (now - last_fullscreen_time) > 1.0:
                press_action_key("f11", "f")
                last_fullscreen_time = now
                action = "Fullscreen Toggle"
            elif fist:
                action = "Fist"
            elif not muted:
                vol_percent = int(np.clip(np.interp(dist, [20, 190], [0, 100]), 0, 100))
                if abs(vol_percent - last_volume) >= 2 and (now - last_volume_commit) > 0.04:
                    vol_ctrl.setVolume(vol_percent)
                    last_volume = vol_percent
                    last_volume_commit = now
                    if vol_percent > 0:
                        last_nonzero_volume = vol_percent
                action = f"Volume {last_volume}%"

            pinch_active = pinch

        dt = max(now - last_frame, 1e-6)
        fps = 1.0 / dt
        smoothed_fps = fps if smoothed_fps == 0 else (0.85 * smoothed_fps + 0.15 * fps)
        last_frame = now

        cv2.putText(frame, f"FPS: {int(smoothed_fps)}", (12, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        cv2.putText(frame, action, (12, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
        cv2.imshow("Media Controller", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
