# GestureFX

GestureFX is a local, real-time hand-gesture visual-effects application. It uses OpenCV for webcam capture, MediaPipe for hand landmarks, NumPy for geometry, and Pygame for lightweight rendering.

## Current status

Milestone 0 is scaffolded. The next implementation step is Milestone 1: safe webcam capture and preview.

## Setup

GestureFX requires Python 3.11 or later. From PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m app.main
```

If `python` opens the Microsoft Store or is unavailable, install Python 3.11+ from python.org and ensure **Add python.exe to PATH** is selected.

After setup, test the camera, hand landmarks, and V1 gesture recognition with:

```powershell
python -m app.main --preview
```

Press `Q` or `Escape` to close the preview safely.

## Privacy

Camera processing is designed to happen locally. GestureFX does not upload or record frames by default.
"# GestureX-" 
