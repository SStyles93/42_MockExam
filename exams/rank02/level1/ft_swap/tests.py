FIXED = [(0, 0), (1, 2), (-5, 5), (2147483647, -2147483648), (42, 42)]


def cases(rng):
    pairs = FIXED + [(rng.randint(-10**6, 10**6), rng.randint(-10**6, 10**6)) for _ in range(15)]
    return [{"args": [a, b], "label": f"a={a}, b={b}; ft_swap(&a, &b)"} for a, b in pairs]
