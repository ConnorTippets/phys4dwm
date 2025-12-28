import math, typing


def add(a: tuple, b: tuple) -> tuple:
    return a[0] + b[0], a[1] + b[1]


def sub(a: tuple, b: tuple) -> tuple:
    return a[0] - b[0], a[1] - b[1]


def div(v: tuple, s: int | float) -> tuple:
    return v[0] / s, v[1] / s


def mul(v: tuple, s: int | float) -> tuple:
    return v[0] * s, v[1] * s


def intersection(
    a: tuple, b: tuple, c: tuple, d: tuple
) -> typing.Literal[False] | tuple[int, int]:
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

    return x1 + t * (x2 - x1), y1 + t * (y2 - y1)


def intersects(a: tuple, b: tuple, c: tuple, d: tuple) -> bool:
    return not intersection(a, b, c, d) is False


def length_sqr(v: tuple) -> float:
    return v[0] ** 2 + v[1] ** 2


def length(v: tuple) -> float:
    return math.sqrt(length_sqr(v))


def unit(v: tuple) -> tuple:
    return div(v, length(v))


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


def ray_aab_intersection(
    v: tuple, dir: tuple, topleft: tuple, size: tuple
) -> tuple[int, int] | typing.Literal[False]:
    try:
        idx = 1 / dir[0]
    except ZeroDivisionError:
        idx = math.inf

    try:
        idy = 1 / dir[1]
    except ZeroDivisionError:
        idy = math.inf

    tx1 = (topleft[0] - v[0]) * idx
    tx2 = (topleft[0] + size[0] - v[0]) * idx

    txnear = min(tx1, tx2)
    txfar = max(tx1, tx2)

    ty1 = (topleft[1] - v[1]) * idy
    ty2 = (topleft[1] + size[1] - v[1]) * idy

    tynear = min(ty1, ty2)
    tyfar = max(ty1, ty2)

    tmin = max(txnear, tynear)
    tmax = min(txfar, tyfar)

    if tmin > tmax:
        return False

    if not tmin < 0:
        return add(v, mul(dir, tmin))
    else:
        return add(v, mul(dir, tmax))


def rotate(v: tuple, angle: float) -> tuple:
    cos = math.cos(math.radians(angle))
    sin = math.sin(math.radians(angle))

    return (
        v[0] * cos - v[1] * sin,
        v[0] * sin + v[1] * cos,
    )


def calc_angular_torque(hit_point: tuple, hit_dir: tuple, impulse_vec: tuple) -> float:
    return (hit_point[0] * impulse_vec[1]) - (hit_point[1] * impulse_vec[0])


def fvti(v: tuple[float, ...]) -> tuple[int, ...]:
    return tuple([int(k) for k in v])


def dot(a: tuple, b: tuple) -> float:
    return a[0] * b[0] + a[1] * b[1]


def cross(a: tuple, b: tuple) -> float:
    return a[0] * b[1] - a[1] * b[0]


def calc_impulse(
    vel: tuple, e: float, normal: tuple, mass: float, moi: float, hit_vector: tuple
) -> float:
    return (-(e + 1) * dot(vel, normal)) / (
        (1 / mass) + (cross(hit_vector, normal) ** 2 / moi)
    )
