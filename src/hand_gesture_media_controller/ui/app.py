import datetime
import os
import sys
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QGuiApplication, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ..core.gesture_utils import is_fist, is_open_palm, is_pinch, is_rock_sign, is_v_sign
from ..core.hand_detector import HandDetector
from ..core.volume_controller import VolumeController
from .splash import SplashScreen


class GestureControllerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hand Gesture Media Controller")
        self.resize(1240, 800)
        self.setMinimumSize(1100, 720)
        self.is_live = False
        self._pulse_on = False
        self.side_mode = False
        self._normal_geometry = None
        self._build_ui()

        self.timer = QTimer(self)
        self.timer.setInterval(16)
        self.timer.timeout.connect(self.update_frame)

        self.pulse_timer = QTimer(self)
        self.pulse_timer.setInterval(420)
        self.pulse_timer.timeout.connect(self._animate_live_indicator)
        self.pulse_timer.start()

        self.cap = None
        self.detector = HandDetector(maxHands=1, detectionCon=0.75, trackCon=0.7, modelComplexity=0)
        self.vol_ctrl = VolumeController()

        self.last_frame_time = time.monotonic()
        self.smoothed_fps = 0.0
        self.process_scale = 0.72

        self.last_volume = 0
        self.last_nonzero_volume = 40
        self.last_volume_commit = 0.0
        self.last_screenshot_time = 0.0
        self.last_media_toggle_time = 0.0
        self.last_mute_toggle_time = 0.0
        self.last_next_track_time = 0.0
        self.last_prev_track_time = 0.0
        self.last_fullscreen_time = 0.0
        self.pinch_active = False
        self.is_muted = False

        project_root = Path(__file__).resolve().parents[3]
        self.screenshot_dir = project_root / "screenshots"
        self.screenshot_dir.mkdir(exist_ok=True)

        self._set_idle_state()

    def _card(self):
        card = QFrame()
        card.setObjectName("panel")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(42)
        shadow.setOffset(0, 10)
        card.setGraphicsEffect(shadow)
        return card

    def _build_ui(self):
        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #030712, stop:0.55 #0f172a, stop:1 #111827);
                color: #e2e8f0;
            }
            QFrame#panel {
                background: rgba(15, 23, 42, 0.84);
                border: 1px solid rgba(96, 165, 250, 0.25);
                border-radius: 20px;
            }
            QLabel#heroTitle {
                font-size: 34px;
                font-weight: 700;
                color: #f8fafc;
            }
            QLabel#heroSub {
                font-size: 15px;
                color: #c7d2fe;
            }
            QLabel#chip {
                background: rgba(30, 41, 59, 0.9);
                border: 1px solid rgba(56, 189, 248, 0.55);
                border-radius: 14px;
                color: #f8fafc;
                padding: 9px 13px;
                font-size: 13px;
                font-weight: 600;
            }
            QLabel#sectionTitle {
                font-size: 17px;
                font-weight: 700;
                color: #f8fafc;
            }
            QLabel#livePill {
                border-radius: 10px;
                padding: 4px 10px;
                font-size: 11px;
                font-weight: 700;
                color: #f8fafc;
            }
            QLabel#videoSurface {
                background: #020617;
                border: 1px solid #334155;
                border-radius: 16px;
                color: #94a3b8;
                font-size: 16px;
                font-weight: 600;
            }
            QLabel#statusMain {
                font-size: 17px;
                font-weight: 700;
                color: #f8fafc;
            }
            QLabel#statusSub {
                font-size: 14px;
                color: #d1d5db;
            }
            QLabel#metaLabel {
                font-size: 13px;
                color: #dbeafe;
            }
            QLabel#metaValue {
                font-size: 14px;
                font-weight: 700;
                color: #f8fafc;
                background: rgba(2, 132, 199, 0.24);
                border-radius: 10px;
                border: 1px solid rgba(56, 189, 248, 0.7);
                padding: 5px 10px;
            }
            QPushButton {
                border-radius: 14px;
                padding: 12px 14px;
                font-size: 13px;
                font-weight: 700;
                border: 1px solid transparent;
            }
            QPushButton#startBtn {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #06b6d4, stop:1 #2563eb);
                color: #ffffff;
            }
            QPushButton#startBtn:hover {
                background: #0284c7;
            }
            QPushButton#stopBtn {
                background: rgba(220, 38, 38, 0.16);
                color: #fecaca;
                border: 1px solid rgba(248, 113, 113, 0.5);
            }
            QPushButton#stopBtn:hover {
                background: rgba(220, 38, 38, 0.3);
            }
            QPushButton#sideBtn {
                background: rgba(30, 64, 175, 0.24);
                color: #dbeafe;
                border: 1px solid rgba(96, 165, 250, 0.75);
            }
            QPushButton#sideBtn:hover {
                background: rgba(37, 99, 235, 0.35);
            }
            QPushButton:disabled {
                background: rgba(100, 116, 139, 0.35);
                color: #cbd5e1;
                border-color: rgba(148, 163, 184, 0.5);
            }
            QProgressBar {
                border: 1px solid rgba(56, 189, 248, 0.7);
                border-radius: 12px;
                text-align: center;
                height: 24px;
                background: rgba(15, 23, 42, 0.9);
                color: #ffffff;
                font-weight: 700;
                font-size: 14px;
            }
            QProgressBar::chunk {
                border-radius: 11px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #0ea5e9, stop:1 #22c55e);
            }
            """
        )

        base_font = QFont("Segoe UI")
        base_font.setPointSize(10)
        self.setFont(base_font)

        self.root = QVBoxLayout()
        self.root.setContentsMargins(24, 24, 24, 24)
        self.root.setSpacing(16)

        self.header_card = self._card()
        header_layout = QVBoxLayout(self.header_card)
        header_layout.setContentsMargins(20, 18, 20, 18)
        header_layout.setSpacing(12)

        title = QLabel("Hand Gesture Media Controller")
        title.setObjectName("heroTitle")
        subtitle = QLabel("A polished real-time dashboard for gesture-powered media control")
        subtitle.setObjectName("heroSub")

        chip_row = QHBoxLayout()
        chip_row.setSpacing(10)
        self.fps_chip = QLabel("FPS: --")
        self.fps_chip.setObjectName("chip")
        self.mode_chip = QLabel("STATE: IDLE")
        self.mode_chip.setObjectName("chip")
        self.action_chip = QLabel("ACTION: WAITING")
        self.action_chip.setObjectName("chip")
        chip_row.addWidget(self.fps_chip)
        chip_row.addWidget(self.mode_chip)
        chip_row.addWidget(self.action_chip)
        chip_row.addStretch()

        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_layout.addLayout(chip_row)

        content = QHBoxLayout()
        content.setSpacing(16)

        self.video_card = self._card()
        video_layout = QVBoxLayout(self.video_card)
        video_layout.setContentsMargins(16, 16, 16, 16)
        video_layout.setSpacing(12)

        video_top = QHBoxLayout()
        feed_title = QLabel("Camera Feed")
        feed_title.setObjectName("sectionTitle")
        self.live_pill = QLabel("OFFLINE")
        self.live_pill.setObjectName("livePill")
        self.mode_pill = QLabel("IDLE")
        self.mode_pill.setObjectName("livePill")
        video_top.addWidget(feed_title)
        video_top.addStretch()
        video_top.addWidget(self.live_pill)
        video_top.addWidget(self.mode_pill)

        self.video_label = QLabel("Camera preview appears here")
        self.video_label.setObjectName("videoSurface")
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(840, 520)
        self.video_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        video_layout.addLayout(video_top)
        video_layout.addWidget(self.video_label)

        side_panel = QVBoxLayout()
        side_panel.setSpacing(12)

        status_card = self._card()
        status_layout = QVBoxLayout(status_card)
        status_layout.setContentsMargins(16, 16, 16, 16)
        status_layout.setSpacing(10)
        status_header = QLabel("System Status")
        status_header.setObjectName("sectionTitle")
        self.status_label = QLabel("Ready to start")
        self.status_label.setObjectName("statusMain")
        self.status_label.setWordWrap(True)
        self.action_detail_label = QLabel("No active gesture yet")
        self.action_detail_label.setObjectName("statusSub")
        self.action_detail_label.setWordWrap(True)
        status_layout.addWidget(status_header)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.action_detail_label)

        stats_card = self._card()
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(16, 16, 16, 16)
        stats_layout.setSpacing(10)
        stats_title = QLabel("Live Metrics")
        stats_title.setObjectName("sectionTitle")
        self.volume_value = QLabel("0%")
        self.volume_value.setObjectName("metaValue")
        self.mute_value = QLabel("UNMUTED")
        self.mute_value.setObjectName("metaValue")
        self.volume_bar = QProgressBar()
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setValue(0)

        volume_label = QLabel("Current volume")
        volume_label.setObjectName("metaLabel")
        mute_label = QLabel("Audio state")
        mute_label.setObjectName("metaLabel")
        stats_layout.addWidget(stats_title)
        stats_layout.addWidget(volume_label)
        stats_layout.addWidget(self.volume_value)
        stats_layout.addWidget(self.volume_bar)
        stats_layout.addWidget(mute_label)
        stats_layout.addWidget(self.mute_value)

        guide_card = self._card()
        guide_layout = QVBoxLayout(guide_card)
        guide_layout.setContentsMargins(16, 16, 16, 16)
        guide_layout.setSpacing(8)
        guide_title = QLabel("Gesture Guide")
        guide_title.setObjectName("sectionTitle")
        guide_1 = QLabel("Pinch: volume / mute")
        guide_2 = QLabel("Tight pinch: screenshot")
        guide_3 = QLabel("Open palm: play/pause")
        guide_4 = QLabel("V sign: next track")
        guide_5 = QLabel("Rock sign: previous track")
        guide_6 = QLabel("Fist: fullscreen toggle")
        for row in (guide_1, guide_2, guide_3, guide_4, guide_5, guide_6):
            row.setObjectName("statusSub")
            row.setWordWrap(True)
            guide_layout.addWidget(row)
        guide_layout.insertWidget(0, guide_title)

        self.start_btn = QPushButton("Start Controller")
        self.start_btn.setObjectName("startBtn")
        self.stop_btn = QPushButton("Stop Controller")
        self.stop_btn.setObjectName("stopBtn")
        self.start_btn.clicked.connect(self.start_controller)
        self.stop_btn.clicked.connect(self.stop_controller)

        self.side_mode_btn = QPushButton("Enable Side Mode")
        self.side_mode_btn.setObjectName("sideBtn")
        self.side_mode_btn.clicked.connect(self._toggle_side_mode)

        self.snap_btn = QPushButton("Snap To Right")
        self.snap_btn.setObjectName("sideBtn")
        self.snap_btn.clicked.connect(self._dock_to_right)

        side_panel.addWidget(status_card)
        side_panel.addWidget(stats_card)
        side_panel.addWidget(guide_card)
        side_panel.addWidget(self.start_btn)
        side_panel.addWidget(self.stop_btn)
        side_panel.addWidget(self.side_mode_btn)
        side_panel.addWidget(self.snap_btn)
        side_panel.addStretch()

        self.side_container = QWidget()
        self.side_container.setLayout(side_panel)
        self.side_container.setFixedWidth(360)

        content.addWidget(self.video_card, 1)
        content.addWidget(self.side_container)

        self.root.addWidget(self.header_card)
        self.root.addLayout(content)
        self.setLayout(self.root)

        self._update_live_badges()

    def _update_live_badges(self):
        if self.is_live:
            self.live_pill.setText("LIVE")
            if self._pulse_on:
                self.live_pill.setStyleSheet("background: #ef4444; color: white; border-radius: 10px; padding: 4px 10px;")
            else:
                self.live_pill.setStyleSheet("background: #7f1d1d; color: #fecaca; border-radius: 10px; padding: 4px 10px;")
            self.mode_pill.setText("RUNNING")
            self.mode_pill.setStyleSheet("background: #0f766e; color: #ccfbf1; border-radius: 10px; padding: 4px 10px;")
        else:
            self.live_pill.setText("OFFLINE")
            self.live_pill.setStyleSheet("background: #1e293b; color: #cbd5e1; border-radius: 10px; padding: 4px 10px;")
            self.mode_pill.setText("IDLE")
            self.mode_pill.setStyleSheet("background: #111827; color: #94a3b8; border-radius: 10px; padding: 4px 10px;")

    def _animate_live_indicator(self):
        self._pulse_on = not self._pulse_on
        self._update_live_badges()

    def _set_idle_state(self):
        self.is_live = False
        self.mode_chip.setText("STATE: IDLE")
        self.action_chip.setText("ACTION: WAITING")
        self.status_label.setText("Ready to start")
        self.action_detail_label.setText("No active gesture yet")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.video_label.clear()
        self.video_label.setText("Camera preview appears here")
        self.volume_bar.setValue(0)
        self.volume_value.setText("0%")
        self.mute_value.setText("UNMUTED")
        self._update_live_badges()

    def _dock_to_right(self):
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geo = screen.availableGeometry()
        x = geo.x() + geo.width() - self.width() - 10
        y = geo.y() + max(10, (geo.height() - self.height()) // 2)
        self.move(x, y)

    def _toggle_side_mode(self):
        was_visible = self.isVisible()
        if not self.side_mode:
            self.side_mode = True
            self._normal_geometry = self.geometry()
            self.header_card.hide()
            self.video_card.hide()
            self.side_container.setFixedWidth(380)
            self.setMinimumSize(380, 620)
            screen = QGuiApplication.primaryScreen()
            if screen is not None:
                h = max(620, min(850, screen.availableGeometry().height() - 20))
            else:
                h = 740
            self.resize(390, h)
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
            if was_visible:
                self.show()
            self._dock_to_right()
            self.raise_()
            self.activateWindow()
            self.side_mode_btn.setText("Disable Side Mode")
            self.action_detail_label.setText("Side mode active: always-on-top media control panel")
        else:
            self.side_mode = False
            self.header_card.show()
            self.video_card.show()
            self.side_container.setFixedWidth(360)
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
            self.setMinimumSize(1100, 720)
            if self._normal_geometry is not None:
                self.setGeometry(self._normal_geometry)
            if was_visible:
                self.show()
            self.side_mode_btn.setText("Enable Side Mode")
            self.action_detail_label.setText("Returned to full dashboard mode")

    def start_controller(self):
        if self.cap is not None:
            return

        backend = cv2.CAP_DSHOW if os.name == "nt" else 0
        self.cap = cv2.VideoCapture(0, backend)

        if not self.cap.isOpened():
            self.status_label.setText("Camera is unavailable")
            self.action_detail_label.setText("Check webcam permissions and close other apps using camera")
            self.cap = None
            return

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        now = time.monotonic()
        self.last_frame_time = now
        self.last_screenshot_time = now - 2.0
        self.last_media_toggle_time = now - 2.0
        self.last_mute_toggle_time = now - 2.0
        self.last_next_track_time = now - 2.0
        self.last_prev_track_time = now - 2.0
        self.last_fullscreen_time = now - 2.0
        self.pinch_active = False

        self.is_live = True
        self.status_label.setText("Gesture tracking started")
        self.action_detail_label.setText("Show your dominant hand in frame")
        self.mode_chip.setText("STATE: RUNNING")
        self.action_chip.setText("ACTION: TRACKING")
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self._update_live_badges()
        self.timer.start()

    def stop_controller(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.timer.stop()
        self._set_idle_state()

    def _save_screenshot_async(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.screenshot_dir / f"screenshot_{timestamp}.png"

        def worker():
            pyautogui.screenshot(str(filename))

        threading.Thread(target=worker, daemon=True).start()

    def _press_action_key(self, preferred_key, fallback_key=None):
        try:
            pyautogui.press(preferred_key)
        except Exception:
            if fallback_key:
                pyautogui.press(fallback_key)

    def _update_volume(self, vol_percent):
        vol_percent = int(np.clip(vol_percent, 0, 100))
        now = time.monotonic()

        if abs(vol_percent - self.last_volume) >= 2 and (now - self.last_volume_commit) > 0.04:
            self.vol_ctrl.setVolume(vol_percent)
            self.last_volume_commit = now
            self.last_volume = vol_percent
            if vol_percent > 0:
                self.last_nonzero_volume = vol_percent

        self.volume_bar.setValue(self.last_volume)
        self.volume_value.setText(f"{self.last_volume}%")

    def _handle_gesture_logic(self, lm_list):
        now = time.monotonic()
        pinch = is_pinch(lm_list, threshold=44)
        tight_pinch = is_pinch(lm_list, threshold=24)
        open_palm = is_open_palm(lm_list)
        v_sign = is_v_sign(lm_list)
        rock_sign = is_rock_sign(lm_list)
        fist = is_fist(lm_list)
        action = "Volume control"

        x1, y1 = lm_list[4][1:]
        x2, y2 = lm_list[8][1:]
        distance = np.hypot(x2 - x1, y2 - y1)

        if tight_pinch and (now - self.last_screenshot_time) > 1.2:
            self._save_screenshot_async()
            self.last_screenshot_time = now
            action = "Screenshot saved"
        elif pinch and not self.pinch_active and (now - self.last_mute_toggle_time) > 0.75:
            if self.is_muted:
                self.vol_ctrl.setVolume(self.last_nonzero_volume)
                self.last_volume = self.last_nonzero_volume
                self.is_muted = False
                action = "Unmuted"
            else:
                self.vol_ctrl.setVolume(0)
                self.last_volume = 0
                self.is_muted = True
                action = "Muted"
            self.volume_bar.setValue(self.last_volume)
            self.last_mute_toggle_time = now
        elif open_palm and (now - self.last_media_toggle_time) > 0.9:
            self._press_action_key("playpause", "space")
            self.last_media_toggle_time = now
            action = "Play/Pause toggled"
        elif open_palm:
            action = "Open palm detected"
        elif v_sign and (now - self.last_next_track_time) > 0.9:
            self._press_action_key("nexttrack", "right")
            self.last_next_track_time = now
            action = "Next track"
        elif v_sign:
            action = "V sign detected"
        elif rock_sign and (now - self.last_prev_track_time) > 0.9:
            self._press_action_key("prevtrack", "left")
            self.last_prev_track_time = now
            action = "Previous track"
        elif rock_sign:
            action = "Rock sign detected"
        elif fist and (now - self.last_fullscreen_time) > 1.0:
            self._press_action_key("f11", "f")
            self.last_fullscreen_time = now
            action = "Fullscreen toggled"
        elif fist:
            action = "Fist detected"
        elif not self.is_muted:
            volume = np.interp(distance, [20, 190], [0, 100])
            self._update_volume(volume)
            action = f"Volume {self.last_volume}%"

        self.pinch_active = pinch
        self.mute_value.setText("MUTED" if self.is_muted else "UNMUTED")
        return action

    def _render_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        qimage = QImage(rgb.data, w, h, ch * w, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qimage))

    def update_frame(self):
        if self.cap is None:
            return

        ok, frame = self.cap.read()
        if not ok:
            self.status_label.setText("Camera frame read failed")
            self.action_detail_label.setText("Retrying frame capture")
            return

        frame = cv2.flip(frame, 1)
        small_frame = cv2.resize(frame, None, fx=self.process_scale, fy=self.process_scale, interpolation=cv2.INTER_LINEAR)

        self.detector.findHands(small_frame, draw=False)
        lm_small = self.detector.findPosition(small_frame)

        action = "Hand not detected"
        if lm_small:
            scale_x = frame.shape[1] / small_frame.shape[1]
            scale_y = frame.shape[0] / small_frame.shape[0]
            lm_list = [(idx, int(x * scale_x), int(y * scale_y)) for idx, x, y in lm_small]
            action = self._handle_gesture_logic(lm_list)

        now = time.monotonic()
        dt = max(now - self.last_frame_time, 1e-6)
        instant_fps = 1.0 / dt
        self.smoothed_fps = instant_fps if self.smoothed_fps == 0 else (0.85 * self.smoothed_fps + 0.15 * instant_fps)
        self.last_frame_time = now

        cv2.putText(frame, f"FPS: {int(self.smoothed_fps)}", (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (95, 245, 225), 2)
        cv2.putText(frame, action, (20, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (245, 200, 80), 2)

        self.fps_chip.setText(f"FPS: {int(self.smoothed_fps)}")
        self.action_chip.setText(f"ACTION: {action.upper()}")
        self.status_label.setText("Tracking hand gestures")
        self.action_detail_label.setText(action)
        self._render_frame(frame)

    def closeEvent(self, event):
        self.stop_controller()
        super().closeEvent(event)


def run_gui():
    app = QApplication(sys.argv)
    splash = SplashScreen()
    window = GestureControllerApp()
    splash.splash_done.connect(window.show)
    splash.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
