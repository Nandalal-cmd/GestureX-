class Trail:
    def __init__(self, length: int = 20):
        self.length = length
        self.points = []

    def push(self, point) -> None:
        self.points.append(point)
        if len(self.points) > self.length:
            self.points.pop(0)

    def clear(self) -> None:
        self.points.clear()

    def render_points(self, width, height):
        return [(int(x * width), int(y * height)) for x, y in self.points]
