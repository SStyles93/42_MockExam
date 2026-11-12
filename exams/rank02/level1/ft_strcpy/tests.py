from engine.testgen import text

FIXED = ["", "a", "hello", "with space", "x" * 500]


def cases(rng):
    strings = FIXED + [text(rng, 0, 100) for _ in range(20)]
    return [{"args": [s], "label": f"ft_strcpy(dst, {s!r})"} for s in strings]
