FIXED = [0, 1, -1, 9, 10, -10, 42, 2147483647, -2147483648, 1000000]


def cases(rng):
    nums = FIXED + [rng.randint(-2147483648, 2147483647) for _ in range(20)]
    return [{"args": [str(n)], "label": f"ft_itoa({n})"} for n in nums]
