FIXED = [0, 1, 2, 3, 4, 6, 8, 1023, 1024, 1025, 2147483648, 4294967295, 65536]


def cases(rng):
    nums = FIXED + [1 << rng.randint(0, 31) for _ in range(10)] \
        + [rng.randint(0, 4294967295) for _ in range(15)]
    return [{"args": [str(n)], "label": f"is_power_of_2({n})"} for n in nums]
