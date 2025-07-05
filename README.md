# Hand Gesture Controlled Media Controller

This project presents a **Python-based, real-time media controller** that leverages **hand gestures** for intuitive system-level control. Built using **OpenCV**, **MediaPipe**, and a **PyQt6 graphical user interface (GUI)**, the application enables users to interact with media functions such as volume control, playback toggling, and screenshot capture through simple hand movements.

---

## 🔹 Key Features

* **Real-time Hand Tracking**
  Utilizes MediaPipe for accurate and responsive gesture recognition via webcam input.

* **Volume Control**
  Adjust system volume dynamically by measuring the distance between the thumb and index finger.

* **Mute/Unmute Functionality**
  Toggle mute status with a soft pinch gesture.

* **Media Playback Control**
  Use an open palm gesture to simulate media play/pause functionality.

* **Screenshot Capture**
  Capture and save screenshots with automatic timestamp naming using a tight pinch gesture.

* **Modern PyQt6 GUI**

  * Live embedded webcam feed
  * Animated splash screen on startup
  * Real-time gesture and FPS display
  * Stylish layout with rounded buttons and shadow effects

---

## 📁 Project Structure

```
HandGestureMediaController/
│
├── main.py                  # Core backend for gesture processing
├── hand_detector.py         # MediaPipe-based hand tracking module
├── volume_controller.py     # System volume control interface
├── gesture_utils.py         # Gesture interpretation utilities
├── gui/
│   ├── app.py               # PyQt6 GUI application with OpenCV feed
│   ├── splash.py            # Splash screen animation
│   └── assets/              # (Optional) GUI images/icons
├── screenshots/             # Auto-saved screenshots from gestures
├── requirements.txt         # List of required Python dependencies
```

---

## 🛠️ Setup Instructions

### Prerequisites

* Python 3.8 or higher
* Webcam-enabled Windows system (volume control requires Windows)

### Installation

1. **Clone or Download the Repository**
   Ensure all files are present in a single directory on your local machine.

2. **Install Dependencies**

   Using the provided `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:

   ```bash
   pip install opencv-python mediapipe pycaw pyautogui PyQt6 numpy
   ```

---

## ▶️ Running the Application

In your terminal or command prompt, navigate to the root folder and run:

```bash
python gui/app.py
```

This will first launch an animated splash screen, followed by the main GUI application window with live webcam integration.

---

## ✋ Gesture Reference Guide

| Gesture                   | Action             |
| ------------------------- | ------------------ |
| Thumb–Index Finger Spread | Increase Volume    |
| Thumb–Index Finger Close  | Mute / Unmute      |
| Open Palm                 | Play / Pause Media |
| Tight Pinch               | Capture Screenshot |

---

## 📌 Additional Notes

* This project was implemented as a learning initiative using concepts and guidance referred from **YouTube tutorials** on hand tracking and OpenCV.
* Designed for Windows OS with webcam input.
* Screenshot files are saved inside the `screenshots/` folder with timestamp-based filenames.

