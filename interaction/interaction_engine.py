"""Translate recognized gestures into effect behaviour."""

from __future__ import annotations

from effects.fire_effect import FireEffect
from gestures.gesture_types import GestureResult, GestureType
from tracking.landmarks import HandLandmarks


class InteractionEngine:
    """Decide which effect reacts to a gesture without rendering anything itself."""

    def __init__(self, fire: FireEffect) -> None:
        self.fire = fire

    def update(self, result: GestureResult, hand: HandLandmarks | None) -> None:
        """Route the gesture to an effect; the fire effect needs the hand location."""
        fire_source = hand.interaction_point if result.gesture is GestureType.FIST and hand else None
        self.fire.set_source(fire_source)

    @property
    def is_engaged(self) -> bool:
        """Return True while an effect is actively reacting to the hand."""
        return self.fire.source is not None