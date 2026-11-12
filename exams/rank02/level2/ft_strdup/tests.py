from engine.testgen import text

FIXED = ["", "a", "hello world", "x" * 1000]


def cases(rng):
    strings = FIXED + [text(rng, 0, 80) for _ in range(20)]
    return [{"args": [s], "label": f"ft_strdup({s!r})"} for s in strings]
