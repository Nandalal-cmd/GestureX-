import pytest

from utils.geometry import average, distance, normalized_to_screen


def test_distance_and_average() -> None:
    assert distance((0.0, 0.0), (0.3, 0.4)) == pytest.approx(0.5)
    assert average(((0.0, 0.0), (1.0, 1.0))) == (0.5, 0.5)


def test_coordinate_conversion_is_centralized() -> None:
    assert normalized_to_screen((0.25, 0.5), 100, 200) == (75, 100)
