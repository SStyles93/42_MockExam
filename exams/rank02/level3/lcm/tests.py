# Values stay small: the subject allows the "try every multiple" method.
FIXED = [(0, 0), (0, 5), (5, 0), (1, 1), (4, 6), (21, 6), (7, 13), (12, 12), (997, 991)]


def cases(rng):
    pairs = list(FIXED) + [(rng.randint(1, 1000), rng.randint(1, 1000)) for _ in range(25)]
    return [{"args": [str(a), str(b)], "label": f"lcm({a}, {b})"} for a, b in pairs]
