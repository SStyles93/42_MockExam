"""Test cases for first_word.

cases(rng) returns a list where each item is either a list of arguments, or a
dict {"args": [...], "stdin": "...", "label": "..."}. Expected output comes
from running the reference solution with the same arguments.
"""
import string

FIXED = [
    [],
    ["hello exam"],
    ["word"],
    [""],
    ["     "],
    ["\t\t  \t"],
    ["   \t  leading blanks"],
    ["trailing   "],
    ["one\ttab"],
    ["!@#$%^ symbols"],
    ["two", "args"],
    ["", ""],
    ["   multiple    spaces   between   "],
]

ALPHABET = string.ascii_letters + string.digits + string.punctuation


def random_sentence(rng):
    parts = []
    for _ in range(rng.randint(0, 6)):
        parts.append(rng.choice(["", " ", "  ", "\t", " \t "]))
        parts.append("".join(rng.choice(ALPHABET) for _ in range(rng.randint(1, 12))))
    parts.append(rng.choice(["", " ", "\t"]))
    return "".join(parts)


def cases(rng):
    return FIXED + [[random_sentence(rng)] for _ in range(40)]
