import math


def add(a: tuple, b: tuple) -> tuple:
    return a[0] + b[0], a[1] + b[1]


def sub(a: tuple, b: tuple) -> tuple:
    return a[0] - b[0], a[1] - b[1]


def in_rect(v: tuple, left: int, top: int, width: int, height: int) -> bool:
    if left < v[0] and v[0] < left + width and top < v[1] and v[1] < top + height:
        return True

    return False


def after_rotation(inner_width: int, inner_height: int, angle: int) -> tuple[int, int]:
    cos = math.cos(math.radians(angle))
    sin = math.sin(math.radians(angle))

    return (
        int(inner_width * abs(cos) + inner_height * abs(sin)),
        int(inner_width * abs(sin) + inner_height * abs(cos)),
    )
