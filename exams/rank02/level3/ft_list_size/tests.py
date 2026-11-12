FIXED = [0, 1, 2, 3, 10, 1000]


def cases(rng):
    sizes = FIXED + [rng.randint(0, 500) for _ in range(10)]
    return [{"args": [str(n)], "label": f"ft_list_size(<list of {n} elements>)"} for n in sizes]
