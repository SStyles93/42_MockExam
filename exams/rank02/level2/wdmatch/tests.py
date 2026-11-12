from engine.testgen import text

FIXED = [[], ["one"], ["a", "b", "c"], ["cat", "a cool hat with a tail"], ["cat", "tac"],
         ["aa", "banana"], ["", "anything"], ["abc", ""], ["", ""], ["abc", "abc"]]


def cases(rng):
    out = list(FIXED)
    for _ in range(30):
        hay = text(rng, 0, 40, "abcdef ")
        if rng.random() < 0.5 and hay:
            needle = "".join(c for c in hay if rng.random() < 0.3)
        else:
            needle = text(rng, 0, 6, "abcdef")
        out.append([needle, hay])
    return out
