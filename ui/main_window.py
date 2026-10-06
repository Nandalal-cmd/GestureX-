class UIState:
    def __init__(self):
        self.mode = "PARTICLE"
        self.running = True
        self.camera_active = False
        self.gesture = "UNKNOWN"
        self.confidence = 0.0
        self.fps = 0.0
        self.particle_count = 0
