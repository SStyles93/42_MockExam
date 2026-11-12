FIXED = [(1, 3), (-1, 2), (0, 0), (0, -3), (5, 5), (-10, -20), (-3, 3)]


def cases(rng):
    pairs = list(FIXED)
    for _ in range(20):
        a = rng.randint(-10**6, 10**6)
        pairs.append((a, a + rng.randint(-200, 200)))
    return [{"args": [str(a), str(b)], "label": f"ft_range({a}, {b})"} for a, b in pairs]
