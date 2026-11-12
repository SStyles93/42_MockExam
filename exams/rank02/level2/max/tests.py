FIXED = [[], [5], [-5], [1, 2, 3], [3, 2, 1], [-3, -2, -1], [7, 7, 7],
         [-2147483648, 2147483647], [0, -1]]


def cases(rng):
    tabs = FIXED + [[rng.randint(-10**9, 10**9) for _ in range(rng.randint(1, 30))]
                    for _ in range(25)]
    return [{"args": [str(n) for n in t], "label": f"max({t}, {len(t)})"} for t in tabs]
