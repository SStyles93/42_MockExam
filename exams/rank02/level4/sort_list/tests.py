FIXED = [[1], [2, 1], [1, 2, 3], [3, 3, 1, 1], [5, -1, 3, -1, 0]]


def cases(rng):
    lists = FIXED + [[rng.randint(-100, 100) for _ in range(rng.randint(1, 40))]
                     for _ in range(20)]
    return [{"args": [str(n) for n in l], "label": f"sort_list({l}) asc, then desc"}
            for l in lists]
