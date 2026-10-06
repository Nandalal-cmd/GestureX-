def smooth(previous, current, factor: float):
    return previous * factor + current * (1.0 - factor)


def smooth_point(previous, current, factor: float):
    return (smooth(previous[0], current[0], factor), smooth(previous[1], current[1], factor))
