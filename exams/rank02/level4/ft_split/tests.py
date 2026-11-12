from engine.testgen import sentence

FIXED = ["", "   ", "one", "one two", "  lead", "trail  ", "a\tb\nc", "\n\n\nx\n\n"]


def cases(rng):
    strings = FIXED + [sentence(rng, blanks=" \t\n") for _ in range(30)]
    return [{"args": [s], "label": f"ft_split({s!r})"} for s in strings]
