# GestureFX

GestureFX is a local, real-time computer-vision project that turns simple hand gestures into interactive visual effects. A webcam frame is processed on your computer, MediaPipe extracts 21 hand landmarks, and the gesture engine interprets those landmarks as hand actions.

The current build provides a camera preview for validating webcam access, single-hand landmarks, palm smoothing, and basic gesture recognition. The particle renderer and visual modes are planned for the following milestone.

## Features available now

- Local webcam capture with safe shutdown
- Single-hand tracking using 21 MediaPipe landmarks
- Smoothed palm interaction point
- Gesture recognition for open palm, fist, pinch, and directional swipes
- Live preview with landmark dots and a gesture/confidence label
- Reusable particle pool with attraction, repulsion, drag, and lifetime recycling
- Unit tests for configuration, geometry, gestures, motion tracking, and particle physics

## Requirements

- Windows 11 (the primary target platform)
- Python 3.11 or newer
- A working webcam

The required Python packages are listed in `requirements.txt`: OpenCV, MediaPipe, NumPy, and Pygame.

## Installation

Open PowerShell in the project folder and run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

If PowerShell prevents activation, allow it for the current terminal session and activate again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## How to operate GestureFX

1. Activate the virtual environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

2. Start the webcam preview:

   ```powershell
   python -m app.main --preview
   ```

3. Grant Windows camera permission if prompted, then place one hand in view of the camera. Keep the palm reasonably well lit and facing the camera.

4. Watch the preview window. Yellow dots represent the detected hand landmarks; the upper-left label shows the recognized gesture and its geometric confidence.

5. Use these gestures:

   | Gesture | How to perform it | Current response |
   | --- | --- | --- |
   | Open palm | Extend all four fingers | Shows `OPEN_PALM` |
   | Fist | Fold most fingers toward the palm | Shows `FIST` |
   | Pinch | Touch the thumb tip to the index-finger tip | Shows `PINCH` |
   | Swipe | Move the hand quickly left, right, up, or down | Emits a directional swipe event |

6. Close the preview by pressing `Q` or `Escape`. The camera is released automatically.

Run the application without the preview option to verify dependency setup only:

```powershell
python -m app.main
```

## Testing

With the virtual environment active, run:

```powershell
python -m pytest -q
```

## Troubleshooting

- **Camera unavailable:** Close other applications that may be using the webcam, then check Windows **Settings → Privacy & security → Camera** and allow desktop apps to access the camera.
- **No landmarks detected:** Improve lighting, keep the full hand in frame, and avoid pointing the palm too far away from the camera.
- **`python` opens Microsoft Store:** Install Python 3.11+ from [python.org](https://www.python.org/downloads/) and select **Add python.exe to PATH** during installation.
- **Missing module errors:** Activate `.venv` and rerun `python -m pip install -r requirements-dev.txt`.

## Privacy

GestureFX processes camera frames locally. It does not upload camera frames, store footage by default, recognize faces, or identify people.

## Project structure

```text
app/        Application entry point and shared configuration
camera/     OpenCV webcam capture
tracking/   MediaPipe adapter and hand landmark models
gestures/   Gesture and swipe recognition
particles/  Reusable particle pool and physics helpers
utils/      Geometry, smoothing, and logging helpers
tests/      Automated unit tests
```

The particle engine is built and unit tested but not yet wired to the camera
preview; gesture-to-particle interaction is the next milestone.
