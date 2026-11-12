"""Random input helpers shared by the exercises' tests.py files.

    from engine.testgen import sentence, word, text, ints
"""
from __future__ import annotations

import string

LETTERS = string.ascii_letters
WORD_CHARS = string.ascii_letters + string.digits + string.punctuation
PRINTABLE = WORD_CHARS + " "


def word(rng, lo: int = 1, hi: int = 10, alphabet: str = WORD_CHARS) -> str:
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(lo, hi)))


def text(rng, lo: int = 0, hi: int = 60, alphabet: str = PRINTABLE) -> str:
    return "".join(rng.choice(alphabet) for _ in range(rng.randint(lo, hi)))


def sentence(rng, max_words: int = 7, blanks: str = " \t", max_run: int = 4,
             edges: bool = True, alphabet: str = WORD_CHARS) -> str:
    """Words separated by runs of blanks, optionally with blanks at both ends."""
    def run():
        return "".join(rng.choice(blanks) for _ in range(rng.randint(1, max_run)))

    words = [word(rng, alphabet=alphabet) for _ in range(rng.randint(1, max_words))]
    out = ""
    for i, w in enumerate(words):
        if i:
            out += run()
        out += w
    if edges and rng.random() < 0.5:
        out = run() + out
    if edges and rng.random() < 0.5:
        out += run()
    return out


def simple_sentence(rng, max_words: int = 7, alphabet: str = WORD_CHARS) -> str:
    """Words separated by exactly one space, no leading/trailing blanks."""
    return " ".join(word(rng, alphabet=alphabet) for _ in range(rng.randint(1, max_words)))


def ints(rng, count: int, lo: int = -1000, hi: int = 1000):
    return [rng.randint(lo, hi) for _ in range(count)]
