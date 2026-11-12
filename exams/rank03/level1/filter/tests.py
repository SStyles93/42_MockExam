from engine.testgen import text

FIXED = [
    {"args": [], "stdin": "abc\n"},
    {"args": [""], "stdin": "abc\n"},
    {"args": ["a", "b"], "stdin": "abc\n"},
    {"args": ["at"], "stdin": "the cat sat on the mat\n"},
    {"args": ["aa"], "stdin": "aaaaa\n"},
    {"args": ["abc"], "stdin": "abababc\n"},
    {"args": ["abc"], "stdin": ""},
    {"args": ["zzz"], "stdin": "nothing to replace here\n"},
    {"args": ["x"], "stdin": "x" * 5000},
    {"args": ["needle"], "stdin": ("hay" * 3000 + "needle") * 30},
    {"args": [" "], "stdin": "spaces   everywhere \n"},
]


def cases(rng):
    out = list(FIXED)
    for _ in range(25):
        alphabet = rng.choice(["ab", "abc", "ab\n", "xyz "])
        pattern = text(rng, 1, 4, alphabet.strip() or "a")
        out.append({"args": [pattern], "stdin": text(rng, 0, rng.choice([50, 2000, 20000]),
                                                     alphabet)})
    for c in out:
        c.setdefault("label", f"./filter {' '.join(repr(a) for a in c['args'])} "
                              f"< ({len(c['stdin'])} bytes of input)")
    return out
