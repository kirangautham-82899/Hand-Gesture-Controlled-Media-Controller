<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&height=220&color=0:0f172a,50:1d4ed8,100:06b6d4&text=Hand%20Gesture%20Media%20Controller&fontColor=ffffff&fontSize=40&fontAlignY=38&desc=Desktop%20Media%20Control%20with%20Real-Time%20AI%20Gestures&descAlignY=58&animation=fadeIn" alt="banner" />
</p>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Segoe+UI&weight=700&size=22&duration=2600&pause=800&color=22D3EE&center=true&vCenter=true&width=980&lines=Control+your+media+with+real-time+hand+gestures;Premium+PyQt6+UI+with+Side+Control+Mode;Optimized+for+smooth+tracking+and+low+latency;Installer+and+GitHub+Release+pipeline+included" alt="typing animation" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Windows_10%2F11-2563EB?style=for-the-badge&logo=windows&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-0EA5E9?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-PyQt6-14B8A6?style=for-the-badge&logo=qt&logoColor=white" />
  <img src="https://img.shields.io/badge/Vision-MediaPipe%20%2B%20OpenCV-16A34A?style=for-the-badge" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/kirangautham-82899/Hand-Gesture-Controlled-Media-Controller?style=flat-square" />
  <img src="https://img.shields.io/github/forks/kirangautham-82899/Hand-Gesture-Controlled-Media-Controller?style=flat-square" />
  <img src="https://img.shields.io/github/last-commit/kirangautham-82899/Hand-Gesture-Controlled-Media-Controller?style=flat-square" />
  <img src="https://img.shields.io/github/repo-size/kirangautham-82899/Hand-Gesture-Controlled-Media-Controller?style=flat-square" />
</p>

---

## What This Project Does

This app turns webcam hand movements into media actions for YouTube, music apps, and local players.  
It runs as a desktop controller with a full dashboard and a compact always-on-top side panel.

### Core capabilities
- Real-time gesture recognition
- Volume control and mute/unmute by pinch behavior
- Playback and track controls with hand signs
- Screenshot capture gesture
- Side mode for controlling media while another app is in focus

---

## Gesture Controls

| Gesture | Action | Trigger Key |
|---|---|---|
| Pinch (thumb + index) | Volume control | System volume API |
| Pinch edge | Mute / Unmute | System volume API |
| Tight pinch | Screenshot | `pyautogui.screenshot()` |
| Open palm | Play / Pause | `playpause` (fallback `space`) |
| V sign | Next track | `nexttrack` (fallback `right`) |
| Rock sign | Previous track | `prevtrack` (fallback `left`) |
| Fist | Fullscreen toggle | `f11` (fallback `f`) |

---

## Interface Modes

### Dashboard Mode
- Full camera feed
- Live FPS / action chips
- Gesture guide + status + metrics

### Side Control Mode
- Compact always-on-top panel
- Designed to stay visible next to YouTube/Spotify/VLC/browser
- Fast access buttons (`Enable Side Mode`, `Snap To Right`)

---

## Project Architecture

```text
HandGestureMediaController/
|- .github/workflows/release-installer.yml
|- installer/HandGestureMediaController.iss
|- scripts/
|  |- build_installer.ps1
|  |- run_camera.py
|  '- run_gui.py
|- src/hand_gesture_media_controller/
|  |- core/
|  |  |- gesture_utils.py
|  |  |- hand_detector.py
|  |  '- volume_controller.py
|  |- ui/
|  |  |- app.py
|  |  '- splash.py
|  '- camera_controller.py
|- requirements.txt
'- README.md
```

---

## Quick Start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts\run_gui.py
```

Optional camera-window mode:
```powershell
python scripts\run_camera.py
```

---

## Build and Release Installer

### Local build
```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_installer.ps1 -Version 1.0.0
```

### GitHub release build
```powershell
git tag v1.0.0
git push origin v1.0.0
```

The GitHub Actions pipeline will:
- build desktop bundle with PyInstaller
- generate installer with Inno Setup
- upload installer artifact to the release

---

## Performance Notes

- Detection runs on downscaled frames to increase FPS.
- Cooldowns prevent repeated accidental triggers.
- Volume updates are throttled to reduce unnecessary system calls.
- Screenshot capture uses a background thread to avoid UI stalls.

---

## Troubleshooting

- Camera not opening:
  - Close Zoom/Teams/OBS and browser camera tabs.
  - Check Windows camera permissions.
- Gesture recognized but no media action:
  - Focus the media app once and retry.
  - Some players respond to fallback keys only.
- Low FPS:
  - Close heavy apps and reduce webcam resolution.

---

## License

Add your preferred open-source license file if you plan to distribute publicly.
