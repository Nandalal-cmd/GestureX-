WRIST = 0
THUMB_TIP = 4
INDEX_TIP = 8
MIDDLE_TIP = 12
RING_TIP = 16
PINKY_TIP = 20

INDEX_MCP = 5
MIDDLE_MCP = 9
RING_MCP = 13
PINKY_MCP = 17

PALM_POINTS = (WRIST, INDEX_MCP, MIDDLE_MCP, RING_MCP, PINKY_MCP)

TIP_PIP_PAIRS = (
    (INDEX_TIP, 6),
    (MIDDLE_TIP, 10),
    (RING_TIP, 14),
    (PINKY_TIP, 18),
)


def palm_center(landmarks):
    xs = [landmarks[i].x for i in PALM_POINTS]
    ys = [landmarks[i].y for i in PALM_POINTS]
    return (sum(xs) / len(xs), sum(ys) / len(ys))
