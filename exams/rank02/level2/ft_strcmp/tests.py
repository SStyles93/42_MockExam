from engine.testgen import text

FIXED = [("", ""), ("a", ""), ("", "a"), ("abc", "abc"), ("abc", "abd"), ("abd", "abc"),
         ("abc", "abcd"), ("abcd", "abc"), ("A", "a"), ("hello", "hellO")]


def cases(rng):
    pairs = list(FIXED)
    for _ in range(30):
        s = text(rng, 0, 20)
        t = s if rng.random() < 0.3 else (s[: rng.randint(0, len(s))] + text(rng, 0, 5))
        pairs.append((s, t))
    return [{"args": [a, b], "label": f"ft_strcmp({a!r}, {b!r})"} for a, b in pairs]
