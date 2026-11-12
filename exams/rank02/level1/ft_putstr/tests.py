from engine.testgen import text

FIXED = ["", "a", "hello world", "tab\there", "two\nlines", "~!@#$%^&*()"]


def cases(rng):
    strings = FIXED + [text(rng, 0, 120) for _ in range(20)]
    return [{"args": [s], "label": f"ft_putstr({s!r})"} for s in strings]
