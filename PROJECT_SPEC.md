# GestureFX — PROJECT_SPEC.md

## AI-Powered Hand Gesture Interactive Visual Effects

**Version:** 1.0  
**Status:** Development Specification  
**Project Type:** Computer Vision + Interactive Graphics + Human-Computer Interaction  
**Primary Platform:** Windows 11  
**Primary Development Environment:** VS Code  
**Primary Coding Agent:** OpenAI Codex  
**Language:** Python 3.11+

---

# 1. Project Overview

GestureFX is a real-time interactive visual application that uses a webcam to detect a user's hand, interpret basic hand gestures and movement, and transform those gestures into visual effects.

The project is NOT intended to be a medical palm-reading system or a traditional hand-recognition application.

The main objective is:

> Turn human hand movement into an interactive digital visual experience.

---

# 2. Core Concept

The system follows this pipeline:

```text
Webcam
   ↓
Camera Processing
   ↓
Hand Detection
   ↓
21 Hand Landmarks
   ↓
Gesture Recognition
   ↓
Interaction Engine
   ↓
Visual Effects Engine
   ↓
Application UI
```

Example:

```text
User opens palm
       ↓
MediaPipe detects hand
       ↓
Landmarks are extracted
       ↓
Gesture engine identifies OPEN_PALM
       ↓
Interaction engine generates particles
       ↓
Particles appear around the hand
```

---

# 3. Project Goals

## Primary Goals

GestureFX must:

1. Detect a user's hand through a webcam.
2. Track hand landmarks in real time.
3. Recognize a small set of predefined gestures.
4. Track hand movement.
5. Convert gestures into visual interactions.
6. Render real-time particles/effects.
7. Provide a simple graphical interface.
8. Display gesture information.
9. Maintain acceptable performance on modest hardware.
10. Be easy to understand and demonstrate.

---

# 4. Non-Goals

The first version must NOT attempt to:

- Recognize every possible hand gesture.
- Train a custom deep-learning model.
- Perform palm reading.
- Perform biometric identification.
- Recognize people's identities.
- Track faces unnecessarily.
- Use large AI models inside the application.
- Build a complex 3D game engine.
- Require cloud processing.
- Require an internet connection after dependencies are installed.

Keep the project lightweight.

---

# 5. Target Hardware

The application should be designed to work on a modest Windows laptop.

Target environment:

```text
OS:
Windows 11

RAM:
8 GB

GPU:
Low-to-mid-range dedicated GPU / integrated fallback

Camera:
Standard laptop USB/webcam

CPU:
Modern x64 processor
```

The application must remain functional even without GPU acceleration.

---

# 6. Technology Stack

## Required

### Python

Primary programming language.

### OpenCV

Responsibilities:

- Webcam capture
- Frame processing
- Image conversion
- Camera status
- Optional camera preview

### MediaPipe

Responsibilities:

- Hand detection
- Hand landmark extraction
- Tracking hand position

### NumPy

Responsibilities:

- Coordinate calculations
- Distance calculations
- Particle calculations
- Vector operations

---

# 7. Rendering Technology

The initial version should use a lightweight 2D renderer.

Preferred option:

```text
Pygame
```

or another lightweight Python-compatible rendering solution.

The renderer must support:

- Particles
- Lines
- Circles
- Trails
- Transparency where practical
- Basic effects
- Real-time rendering

Do NOT introduce a heavy game engine unless there is a clear technical reason.

---

# 8. GUI

The project should have a simple professional interface.

Possible technology:

```text
PySide6
```

or another lightweight Python GUI framework.

The GUI should not interfere with real-time rendering.

Recommended structure:

```text
Main Window
├── Visual Canvas
├── Gesture Status
├── Confidence
├── FPS
├── Particle Count
├── Current Mode
├── Camera Status
└── Settings
```

---

# 9. Supported Gestures — V1

Only implement the following gestures initially.

## 9.1 OPEN_PALM

Detection concept:

- Fingers extended.
- Thumb reasonably separated.
- Palm area visible.

Action:

```text
Generate / activate particles around the hand.
```

## 9.2 FIST

Detection concept:

- Fingers folded toward palm.
- Finger-tip distances indicate closed hand.

Action:

```text
Compress nearby particles toward the hand.
```

## 9.3 PINCH

Detection:

Measure distance between thumb tip and index finger tip.

```text
If distance is below a configurable threshold:
    PINCH = TRUE
```

Action:

```text
Attract particles toward the pinch point.
```

## 9.4 SWIPE

Possible gestures:

```text
SWIPE_LEFT
SWIPE_RIGHT
SWIPE_UP
SWIPE_DOWN
```

Track hand position over time and calculate:

```text
dx
dy
velocity
```

If movement exceeds configurable thresholds, detect a swipe.

Action:

```text
Particles receive directional velocity.
```

---

# 10. Gesture State Model

The application should distinguish between:

```text
UNKNOWN
OPEN_PALM
FIST
PINCH
SWIPE_LEFT
SWIPE_RIGHT
SWIPE_UP
SWIPE_DOWN
```

Do not trigger effects continuously for gestures that should be event-based.

OPEN_PALM can be continuous.

SWIPE should be treated as an event.

---

# 11. Gesture Confidence

Every recognized gesture should have a confidence-like score.

Example:

```text
Gesture: PINCH
Confidence: 94%
```

The confidence does not need to come from an ML classifier.

It may be calculated from geometric conditions and must be clamped between 0.0 and 1.0.

---

# 12. Hand Tracking

MediaPipe provides approximately 21 landmarks.

Important landmarks include:

```text
0  = Wrist
4  = Thumb Tip
8  = Index Finger Tip
12 = Middle Finger Tip
16 = Ring Finger Tip
20 = Pinky Tip
```

Use normalized coordinates where possible:

```text
x = 0.0 → 1.0
y = 0.0 → 1.0
```

This makes the system independent of camera resolution.

---

# 13. Coordinate System

Camera coordinates:

```text
x → horizontal
y → vertical
```

Rendering coordinates:

```text
screen_x
screen_y
```

The conversion should be centralized.

Do NOT scatter coordinate conversion logic throughout the project.

---

# 14. Hand Position

Use a stable reference point for general hand interaction.

Preferred initial reference:

```text
Palm center
```

Calculate palm center using several landmarks rather than relying exclusively on one landmark.

Suggested points:

```text
wrist
index MCP
middle MCP
ring MCP
pinky MCP
```

Average these positions.

---

# 15. Motion Tracking

Track:

```text
current_position
previous_position
velocity
direction
speed
```

Example:

```text
velocity_x = current_x - previous_x
velocity_y = current_y - previous_y
```

Apply smoothing to reduce jitter.

---

# 16. Smoothing

Raw webcam tracking may be noisy.

Implement lightweight smoothing:

```text
smoothed_position =
    previous_position * smoothing_factor
    +
    current_position * (1 - smoothing_factor)
```

The smoothing factor must be configurable.

Default should prioritize responsiveness over excessive smoothing.

---

# 17. Particle System

The particle system is the primary visual component.

Each particle should have at least:

```text
x
y
vx
vy
size
life
max_life
opacity
```

Optional properties can be added only when needed:

```text
rotation
mass
drag
noise
```

---

# 18. Particle Count

Initial target:

```text
500–1000 particles
```

Maximum configurable target:

```text
2000 particles
```

Avoid creating thousands of new Python objects every frame unnecessarily.

Reuse particle objects where practical.

---

# 19. Particle Physics

Particles should support:

### Attraction

Particles move toward a target.

```text
force → target - particle
```

### Repulsion

Particles move away from the hand.

```text
force → particle - target
```

### Velocity

Particles retain movement.

### Drag

Velocity slowly decreases.

### Lifetime

Particles eventually disappear or recycle.

---

# 20. Gesture → Particle Mapping

## OPEN_PALM

```text
Generate particles
+
Particles orbit/follow palm
+
Small outward movement
```

## PINCH

```text
Find pinch point
↓
Calculate particle distance
↓
Apply attraction force
↓
Particles gather around pinch
```

## FIST

```text
Find palm center
↓
Strong attraction
↓
Particles compress
↓
Create compact energy ball
```

## SWIPE

```text
Detect swipe direction
↓
Apply directional impulse
↓
Particles fly in swipe direction
↓
Slowly return to normal physics
```

---

# 21. Gesture Trail

Display a fading trail following hand movement.

Maintain a small position history and render it with decreasing opacity/size.

The trail must disappear naturally when the hand stops moving.

---

# 22. Visual Mode 1 — PARTICLE

Default mode.

Characteristics:

- Floating particles
- Hand attraction
- Hand movement interaction
- Trails
- Gesture-based particle behavior

This should be the most stable mode.

---

# 23. Visual Mode 2 — ENERGY

Energy mode should make particles appear more concentrated around the hand.

Possible effects:

```text
Particle ring
Energy arcs
Small bursts
Hand glow
Motion trails
```

Do not implement expensive post-processing initially.

Simple geometry can create the effect.

---

# 24. Visual Mode 3 — GALAXY

Galaxy mode represents particles as an orbiting system.

Concept:

```text
             •
       •             •

            HAND
       •             •

             •
```

Possible interactions:

```text
Open palm → stable orbit
Pinch → compress orbit
Fist → collapse galaxy
Swipe → disturb orbit
```

---

# 25. UI Requirements

The application should show:

```text
GestureFX

Camera: ACTIVE

Gesture:
OPEN PALM

Confidence:
94%

Mode:
PARTICLE

Particles:
842

FPS:
58
```

Buttons:

```text
[ PARTICLE ]
[ ENERGY ]
[ GALAXY ]
[ START ]
[ STOP ]
```

Optional:

```text
[ SETTINGS ]
```

---

# 26. Settings

V1 settings:

```text
Particle Count
Gesture Sensitivity
Smoothing
Trail Length
Effect Strength
```

Use reasonable defaults.

Do not build a complicated settings system.

---

# 27. FPS

Display real-time FPS.

Target:

```text
30 FPS minimum
```

Preferred:

```text
45–60 FPS
```

If FPS drops:

1. Reduce particle count.
2. Reduce expensive calculations.
3. Reduce rendering complexity.
4. Avoid unnecessary allocations.
5. Profile before making major changes.

---

# 28. Camera Handling

If the camera is available:

```text
Camera: ACTIVE
```

If unavailable:

```text
Camera unavailable.

Please connect or enable a webcam.
```

Do not crash.

---

# 29. Error Handling

Gracefully handle:

- Camera unavailable
- MediaPipe initialization failure
- Invalid configuration
- Missing dependencies
- Rendering errors where recoverable
- Unsupported camera resolution

Errors should be logged.

The UI should display user-friendly messages.

---

# 30. Logging

Use Python's standard logging system.

Levels:

```text
DEBUG
INFO
WARNING
ERROR
```

Avoid excessive console output every frame.

Do NOT print thousands of messages per second.

---

# 31. Proposed Folder Structure

```text
GestureFX/
│
├── README.md
├── PROJECT_SPEC.md
├── requirements.txt
├── .gitignore
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── config.py
│
├── camera/
│   ├── __init__.py
│   └── camera.py
│
├── tracking/
│   ├── __init__.py
│   ├── hand_tracker.py
│   └── landmarks.py
│
├── gestures/
│   ├── __init__.py
│   ├── gesture_detector.py
│   ├── gesture_types.py
│   └── motion_tracker.py
│
├── interaction/
│   ├── __init__.py
│   └── interaction_engine.py
│
├── particles/
│   ├── __init__.py
│   ├── particle.py
│   ├── particle_system.py
│   └── physics.py
│
├── effects/
│   ├── __init__.py
│   ├── particle_effect.py
│   ├── energy_effect.py
│   ├── galaxy_effect.py
│   └── trails.py
│
├── rendering/
│   ├── __init__.py
│   └── renderer.py
│
├── ui/
│   ├── __init__.py
│   ├── main_window.py
│   └── widgets.py
│
├── utils/
│   ├── __init__.py
│   ├── geometry.py
│   ├── smoothing.py
│   └── logger.py
│
├── tests/
│   ├── test_gestures.py
│   ├── test_geometry.py
│   ├── test_motion.py
│   └── test_particles.py
│
└── assets/
    └── ...
```

---

# 32. Architecture Rules

Camera code must NOT know about particles.

Tracking code must NOT know about UI.

Gesture detection must NOT directly render effects.

Particle system must NOT directly access the webcam.

UI should communicate through application state/interfaces.

Preferred dependency flow:

```text
Camera
   ↓
Tracking
   ↓
Gestures
   ↓
Interaction
   ↓
Effects
   ↓
Renderer
   ↓
UI
```

Avoid circular dependencies.

---

# 33. Configuration

Centralize configuration.

Example:

```python
CAMERA_INDEX = 0
MAX_PARTICLES = 2000
DEFAULT_PARTICLES = 800
GESTURE_SENSITIVITY = 0.5
SMOOTHING_FACTOR = 0.65
TRAIL_LENGTH = 20
TARGET_FPS = 60
```

Do not hard-code these values throughout the project.

---

# 34. Testing Strategy

Every major module should be independently testable.

Test:

```text
Distance calculations
Angle calculations
Finger states
Gesture detection
Swipe detection
Motion smoothing
Particle physics
Particle lifetime
Configuration
```

Camera testing may require manual testing.

---

# 35. Development Milestones

## Milestone 0 — Project Setup

Estimated: 0.5–1 day

Tasks:

- Create repository.
- Create Python environment.
- Install dependencies.
- Create folder structure.
- Add PROJECT_SPEC.md.
- Create basic application entry point.

## Milestone 1 — Webcam

Estimated: 1 day

Deliverable:

```text
Webcam opens
+
Frames display
+
Camera can close safely
```

## Milestone 2 — Hand Tracking

Estimated: 1–2 days

Deliverable:

```text
MediaPipe
+
21 landmarks
+
Palm position
+
Basic smoothing
```

## Milestone 3 — Gesture Engine

Estimated: 2–3 days

Deliverable:

```text
OPEN_PALM
FIST
PINCH
SWIPE
```

## Milestone 4 — Particle Engine

Estimated: 2–4 days

Deliverable:

```text
Particle generation
+
Physics
+
Attraction
+
Repulsion
+
Lifetime
```

## Milestone 5 — Gesture Interaction

Estimated: 2–3 days

Deliverable:

```text
Hand controls particles.
```

## Milestone 6 — Trails

Estimated: 1 day

Deliverable:

```text
Smooth hand movement trails.
```

## Milestone 7 — Visual Modes

Estimated: 2–4 days

Deliverable:

```text
PARTICLE
ENERGY
GALAXY
```

## Milestone 8 — GUI

Estimated: 2–3 days

Deliverable:

```text
Professional application interface.
```

## Milestone 9 — Optimization

Estimated: 1–2 days

Deliverable:

```text
Stable 30–60 FPS.
```

## Milestone 10 — Testing & Documentation

Estimated: 2–3 days

Deliverable:

```text
README
Tests
Screenshots
Demo
Project documentation
```

---

# 36. Agentic Development Rules

This project will be developed primarily using OpenAI Codex and other coding agents.

Agents MUST follow these rules.

## Rule 1 — Read the specification first

Before making changes:

```text
Read PROJECT_SPEC.md
```

## Rule 2 — Work on one milestone at a time

Do not implement the entire project in one operation.

## Rule 3 — Inspect before modifying

Before changing existing code:

```text
Inspect relevant files.
Understand existing architecture.
Then modify.
```

## Rule 4 — Preserve working functionality

Do not rewrite working modules unnecessarily.

## Rule 5 — Minimal changes

Prefer the smallest change that solves the task.

## Rule 6 — Test after implementation

After each significant change:

```text
Run tests
+
Run application
+
Check relevant behavior
```

## Rule 7 — Do not invent dependencies

Before adding a package:

1. Determine whether it is necessary.
2. Prefer existing dependencies.
3. Explain why the package is required.
4. Update requirements.txt.

## Rule 8 — No unnecessary architecture changes

Do not introduce:

```text
Microservices
Databases
Cloud infrastructure
Large ML frameworks
Complex state management
```

unless specifically required later.

---

# 37. Codex Prompt Template

Use this structure when giving Codex tasks:

```text
You are working on GestureFX.

First read:
- PROJECT_SPEC.md
- README.md
- relevant existing source files

Current milestone:
[MILESTONE NAME]

Task:
[EXACT TASK]

Requirements:
- Follow PROJECT_SPEC.md.
- Preserve existing working behavior.
- Do not unnecessarily change architecture.
- Keep dependencies lightweight.
- Write clean modular Python.
- Add/update tests where appropriate.

Before coding:
1. Inspect the existing implementation.
2. Identify the files that need modification.
3. Briefly explain the planned changes.

Then implement the task.

After implementation:
1. Run relevant tests.
2. Run static checks if available.
3. Verify the application behavior.
4. Report files changed.
5. Report tests performed.
6. Report any remaining issues.
```

---

# 38. Important Agent Constraint

Agents must NOT continuously expand the project scope.

Features such as:

```text
Face recognition
Voice control
AI-generated effects
3D rendering
Cloud synchronization
Multi-user tracking
```

are future features unless explicitly approved.

---

# 39. Future Features

Potential V2/V3 features:

```text
Two-hand interaction
Custom gestures
Gesture recording
Gesture editor
Music-reactive particles
Microphone input
3D effects
WebGL renderer
AR-style effects
Custom particle presets
Gesture macros
Screen interaction
Presentation control
Voice + gesture combination
```

These are NOT part of V1.

---

# 40. Security & Privacy

The application should process camera data locally.

The application must NOT:

- Upload camera frames.
- Store camera footage by default.
- Perform facial recognition.
- Send biometric information to external servers.

Camera access should only occur while the application is running and camera functionality is enabled.

---

# 41. Performance Principles

Prioritize:

```text
Responsiveness
+
Stable FPS
+
Low memory usage
+
Simple calculations
```

Avoid premature optimization.

Profile before optimizing.

Do not sacrifice maintainability merely to gain a small performance improvement.

---

# 42. Definition of Done

GestureFX V1 is complete when a user can:

```text
1. Launch the application.
2. Enable the webcam.
3. Place a hand in front of the camera.
4. See the hand tracked.
5. Open the palm.
6. See particles appear.
7. Move the hand.
8. See particles respond.
9. Pinch.
10. See particles gather around the pinch.
11. Make a fist.
12. See particles collapse.
13. Swipe.
14. See particles move in the swipe direction.
15. Switch between visual modes.
16. See gesture information and FPS.
17. Close the application without errors.
```

---

# 43. Final Product Vision

GestureFX should feel like a small interactive art installation rather than a basic computer-vision demo.

The user should experience:

```text
Physical movement
       ↓
Computer vision
       ↓
Gesture understanding
       ↓
Digital reaction
       ↓
Visual feedback
```

The project succeeds when the user can naturally move their hand and feel that they are controlling a digital visual environment with their body.

---

# 44. Development Priority

Always prioritize in this order:

```text
1. Correctness
2. Stability
3. Responsiveness
4. Visual quality
5. UI polish
6. Additional features
```

Do not add visual complexity before the underlying interaction is reliable.

---

# 45. Current Development Target

The immediate development target is:

```text
MILESTONE 0
↓
MILESTONE 1
↓
MILESTONE 2
↓
MILESTONE 3
```

begin Energy Mode, Galaxy Mode, advanced UI, or other future features until the hand-to-particle interaction works reliably.

---

# END OF PROJECT SPECIFICATION
