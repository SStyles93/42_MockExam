from engine.testgen import sentence

FIXED = [
    [], ["only one"], ["two", "args"], ["a", "b", "c", "d"],
    ["banana bread", "a", "o"], ["banana", "x", "y"], ["banana", "an", "o"],
    ["banana", "a", "on"], ["", "a", "b"], ["aaaa", "a", "a"], ["Case Sensitive", "s", "Z"],
]
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def cases(rng):
    out = list(FIXED)
    for _ in range(30):
        s = sentence(rng, blanks=" ", alphabet=LETTERS + "0123456789 ,.!")
        present = [c for c in s if c in LETTERS]
        search = rng.choice(present) if present and rng.random() < 0.8 else rng.choice(LETTERS)
        out.append([s, search, rng.choice(LETTERS)])
    return out
