FIXED = [[1], [2, 1], [1, 2], [3, 3, 3], [5, -1, 3, -1, 0],
         [2147483647, -2147483648, 0]]


def cases(rng):
    tabs = FIXED + [[rng.randint(-1000, 1000) for _ in range(rng.randint(1, 60))]
                    for _ in range(20)]
    return [{"args": [str(n) for n in t], "label": f"sort_int_tab({t}, {len(t)})"} for t in tabs]
