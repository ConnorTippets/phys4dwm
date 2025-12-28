import math


def add(a: tuple, b: tuple) -> tuple:
    return a[0] + b[0], a[1] + b[1]


def sub(a: tuple, b: tuple) -> tuple:
    return a[0] - b[0], a[1] - b[1]


def div(v: tuple, s: int) -> tuple:
    return v[0] / s, v[1] / s


def in_rect(v: tuple, left: int, top: int, width: int, height: int) -> bool:
    if left < v[0] and v[0] < left + width and top < v[1] and v[1] < top + height:
        return True

    return False


def rotate(v: tuple, angle: int) -> tuple:
    cos = math.cos(math.radians(angle))
    sin = math.sin(math.radians(angle))

    return (
        int(v[0] * abs(cos) + v[1] * abs(sin)),
        int(v[0] * abs(sin) - v[1] * abs(cos)),
    )
