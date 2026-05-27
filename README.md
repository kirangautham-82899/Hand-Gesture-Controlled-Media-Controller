# Hand Gesture Media Controller

Control media playback, volume, and quick actions using real-time hand gestures from your webcam.

## Highlights
- Real-time hand tracking with MediaPipe + OpenCV
- Premium PyQt6 desktop dashboard UI
- Side-panel mode for always-on-top media control
- Gesture-based volume, mute, playback, track skip, fullscreen, and screenshot
- Optimized loop for smoother FPS and lower latency
- Windows installer + GitHub Release automation included

## Gesture Map
- `Pinch` (thumb + index): live volume control
- `Pinch edge` (enter pinch): mute / unmute toggle
- `Tight pinch`: screenshot
- `Open palm`: play / pause
- `V sign`: next track
- `Rock sign`: previous track
- `Fist`: fullscreen toggle

## Project Structure
```text
HandGestureMediaController/
|- .github/
|  '- workflows/
|     '- release-installer.yml
|- installer/
|  '- HandGestureMediaController.iss
|- scripts/
|  |- build_installer.ps1
|  |- run_camera.py
|  '- run_gui.py
|- screenshots/
|  '- .gitkeep
|- src/
|  '- hand_gesture_media_controller/
|     |- core/
|     |  |- gesture_utils.py
|     |  |- hand_detector.py
|     |  '- volume_controller.py
|     |- ui/
|     |  |- app.py
|     |  '- splash.py
|     |- camera_controller.py
|     '- __main__.py
|- main.py
|- requirements.txt
'- README.md
```

## Quick Start

### 1) Create virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install dependencies
```powershell
pip install -r requirements.txt
```

### 3) Run app
```powershell
python scripts\run_gui.py
```

Optional camera-window mode:
```powershell
python scripts\run_camera.py
```

## Side-Panel Workflow (Recommended)
1. Start the controller in GUI mode.
2. Click `Enable Side Mode`.
3. Keep the panel docked right while using YouTube/Spotify/VLC/etc.
4. Use gestures without leaving your media window.

## Performance Notes
- Hand detection runs on a downscaled frame for speed.
- Cooldowns prevent accidental repeated triggers.
- Volume updates are throttled to avoid noisy system calls.
- Screenshot capture runs in a background thread.

## Build Windows Installer

### Local build
Install Inno Setup 6, then:
```powershell
powershell -ExecutionPolicy Bypass -File scripts\build_installer.ps1 -Version 1.0.0
```
Output:
```text
dist_installer/HandGestureMediaController-Setup-1.0.0.exe
```

### Auto-build on GitHub release tag
```powershell
git tag v1.0.0
git push origin v1.0.0
```
The workflow in `.github/workflows/release-installer.yml` builds and uploads the installer artifact to the release.

## Requirements
- Windows 10/11
- Python 3.10+ (3.11 recommended)
- Webcam
- Audio output device

## Troubleshooting
- If camera fails: close Zoom/Teams/OBS/browser camera tabs and retry.
- If media keys do not affect a player: focus the player once, then retry gestures.
- If FPS is low: reduce camera resolution or close heavy background apps.

## License
Use this project for personal or educational purposes. Add your preferred open-source license file if you plan to distribute broadly.
