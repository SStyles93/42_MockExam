from engine.testgen import text

FIXED = ["", "a", "ab", "abc", "racecar", "Hello, World!"]


def cases(rng):
    strings = FIXED + [text(rng, 0, 60) for _ in range(20)]
    return [{"args": [s], "label": f"ft_strrev({s!r})"} for s in strings]
