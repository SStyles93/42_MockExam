from engine.testgen import text

FIXED = [("", ""), ("abc", ""), ("", "abc"), ("hello world", " "), ("hello", "xyz"),
         ("hello", "o"), ("hello", "h"), ("a,b;c", ";,")]


def cases(rng):
    pairs = list(FIXED) + [(text(rng, 0, 40), text(rng, 0, 6)) for _ in range(30)]
    return [{"args": [s, r], "label": f"ft_strcspn({s!r}, {r!r})"} for s, r in pairs]
