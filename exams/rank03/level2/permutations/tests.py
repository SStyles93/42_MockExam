import string

FIXED = ["a", "ab", "ba", "abc", "cab", "dcba", "zyx"]


def cases(rng):
    words = list(FIXED)
    for _ in range(15):
        words.append("".join(rng.sample(string.ascii_lowercase, rng.randint(1, 7))))
    return [[w] for w in words]
