FIXED = [
    ("%d", "42"), ("%d", "  -17 rest"), ("%d", "+8"), ("%d", "abc"), ("%d %d", "1 2"),
    ("%d %d", "1\n\n  2"), ("%d%d", "1 2"), ("%d %d %d", "1 2 x"), ("%s", "hello world"),
    ("%s %s", "a b"), ("%s%s", "first\tsecond"), ("%c", " x"), ("%c%c", "ab"), (" %c", "   z"),
    ("%d %s %c", "42 word x"), ("%s%d", "abc 12"), ("x%dy", "x5y"), ("x%d", "y5"),
    ("%d,%d", "3,4"), ("%d,%d", "3;4"), ("%d", ""), ("%s", ""), ("%c", ""), ("%c%d", "a12"),
    ("%d%c", "12a"), ("%d %c", "12   a"), ("%s,%d", "word,5"),
]
WORDS = ["hello", "x", "42abc", "a,b", "UPPER", "under_score"]


def piece(conv, rng):
    if conv == "d":
        return str(rng.randint(-100000, 100000))
    if conv == "s":
        return rng.choice(WORDS)
    return rng.choice("abcXYZ09,")


def cases(rng):
    pairs = list(FIXED)
    for _ in range(30):
        convs = [rng.choice("dsc") for _ in range(rng.randint(1, 4))]
        seps = [rng.choice([" ", ",", "", "\n"]) for _ in convs]
        fmt = "".join(("%" + c) + (s if i < len(convs) - 1 else "")
                      for i, (c, s) in enumerate(zip(convs, seps)))
        inp = ""
        for i, c in enumerate(convs):
            inp += piece(c, rng)
            if i < len(convs) - 1:
                sep = seps[i]
                inp += sep if sep.strip() else rng.choice([" ", "  ", "\n", ""])
        if rng.random() < 0.2 and len(inp) > 1:
            cut = rng.randint(1, len(inp) - 1)
            inp = inp[:cut]
            if not inp.strip():
                inp = "z"
        pairs.append((fmt, inp))
    return [{"args": [f], "stdin": s, "label": f"ft_scanf({f!r}, ...) with input {s!r}"}
            for f, s in pairs]
