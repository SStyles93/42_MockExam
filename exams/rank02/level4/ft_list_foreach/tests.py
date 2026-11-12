FIXED = [[], [1], [1, 2, 3], [-5, 0, 5]]


def cases(rng):
    lists = FIXED + [[rng.randint(-1000, 1000) for _ in range(rng.randint(1, 30))]
                     for _ in range(15)]
    return [{"args": [str(n) for n in l], "label": f"list {l}: print, double, print"}
            for l in lists]
