import math


def add(a: tuple, b: tuple) -> tuple:
    return a[0] + b[0], a[1] + b[1]


def sub(a: tuple, b: tuple) -> tuple:
    return a[0] - b[0], a[1] - b[1]


def div(v: tuple, s: int) -> tuple:
    return v[0] / s, v[1] / s


def intersects(a: tuple, b: tuple, c: tuple, d: tuple) -> bool:
    x1, y1 = a
    x2, y2 = b
    x3, y3 = c
    x4, y4 = d

    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if den == 0:
        return False

    t_num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
    t = t_num / den

    u_num = (x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)
    u = -(u_num / den)

    intersecting = (t >= 0) and (0 <= u <= 1)
    if not intersecting:
        return False

    return True


def in_rect(
    v: tuple, topleft: tuple, topright: tuple, bottomright: tuple, bottomleft: tuple
) -> bool:
    minx = min(topleft[0], topright[0], bottomright[0], bottomleft[0])
    maxx = max(topleft[0], topright[0], bottomright[0], bottomleft[0])
    miny = min(topleft[1], topright[1], bottomright[1], bottomleft[1])
    maxy = max(topleft[1], topright[1], bottomright[1], bottomleft[1])

    # bounds check
    if not (minx < v[0] and v[0] < maxx and miny < v[1] and v[1] < maxy):
        return False

    intersections = 0
    for wall_a, wall_b in (
        (topleft, topright),
        (topright, bottomright),
        (bottomright, bottomleft),
        (bottomleft, topleft),
    ):
        intersections += intersects(v, add(v, (1, 0)), wall_a, wall_b)

    return not (intersections % 2) == 0


def rotate(v: tuple, angle: int) -> tuple:
    cos = math.cos(math.radians(angle))
    sin = math.sin(math.radians(angle))

    return (
        int(v[0] * cos - v[1] * sin),
        int(v[0] * sin + v[1] * cos),
    )
