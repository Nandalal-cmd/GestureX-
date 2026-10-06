from enum import Enum


class GestureType(str, Enum):
    UNKNOWN = "UNKNOWN"
    OPEN_PALM = "OPEN_PALM"
    FIST = "FIST"
    PINCH = "PINCH"
    SWIPE_LEFT = "SWIPE_LEFT"
    SWIPE_RIGHT = "SWIPE_RIGHT"
    SWIPE_UP = "SWIPE_UP"
    SWIPE_DOWN = "SWIPE_DOWN"


SWIPES = {GestureType.SWIPE_LEFT, GestureType.SWIPE_RIGHT, GestureType.SWIPE_UP, GestureType.SWIPE_DOWN}
