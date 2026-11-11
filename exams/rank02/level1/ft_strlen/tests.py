"""Test cases for ft_strlen. Each argument is passed through main.c."""
import string

FIXED = ["", "a", "hello", "hello world", " ", "\t\n", "42", "x" * 1000]


def label(s):
    return f"ft_strlen({s!r})"


def cases(rng):
    strings = FIXED + [
        "".join(rng.choice(string.printable) for _ in range(rng.randint(0, 300)))
        for _ in range(30)
    ]
    return [{"args": [s], "label": label(s)} for s in strings]
