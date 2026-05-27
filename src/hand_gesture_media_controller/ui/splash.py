from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QGraphicsOpacityEffect, QLabel, QProgressBar, QVBoxLayout, QWidget


class SplashScreen(QWidget):
    splash_done = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Launching")
        self.setFixedSize(920, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self.setStyleSheet(
            """
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #020617, stop:0.5 #0f172a, stop:1 #1e293b);
                color: #e2e8f0;
            }
            QFrame {
                border: 1px solid rgba(96, 165, 250, 0.35);
                border-radius: 18px;
                background: rgba(15, 23, 42, 0.82);
            }
            QLabel#headline {
                font-size: 36px;
                font-weight: 700;
                color: #f8fafc;
            }
            QLabel#sub {
                font-size: 14px;
                color: #94a3b8;
            }
            QProgressBar {
                border: 1px solid rgba(56, 189, 248, 0.45);
                border-radius: 10px;
                text-align: center;
                height: 20px;
                color: #e2e8f0;
                background: rgba(15, 23, 42, 0.92);
                font-weight: 700;
            }
            QProgressBar::chunk {
                border-radius: 9px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #06b6d4, stop:1 #2563eb);
            }
            """
        )

        self.setFont(QFont("Segoe UI"))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(34, 34, 34, 34)

        card = QFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(36, 36, 36, 36)
        card_layout.setSpacing(14)

        self.headline = QLabel("Hand Gesture Controller")
        self.headline.setObjectName("headline")
        self.headline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.subline = QLabel("Loading camera stack and gesture engine")
        self.subline.setObjectName("sub")
        self.subline.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(10)
        self.progress.setTextVisible(True)

        card_layout.addStretch()
        card_layout.addWidget(self.headline)
        card_layout.addWidget(self.subline)
        card_layout.addWidget(self.progress)
        card_layout.addStretch()
        layout.addWidget(card)

        opacity = QGraphicsOpacityEffect()
        card.setGraphicsEffect(opacity)
        self.fade_animation = QPropertyAnimation(opacity, b"opacity")
        self.fade_animation.setDuration(1350)
        self.fade_animation.setStartValue(0.12)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.fade_animation.start()

        self.progress_timer = QTimer(self)
        self.progress_timer.setInterval(80)
        self.progress_timer.timeout.connect(self._advance_progress)
        self.progress_timer.start()

        QTimer.singleShot(2200, self.finish_splash)

    def _advance_progress(self):
        nxt = min(self.progress.value() + 4, 100)
        self.progress.setValue(nxt)

    def finish_splash(self):
        self.progress_timer.stop()
        self.close()
        self.splash_done.emit()
