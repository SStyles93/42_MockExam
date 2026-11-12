from engine.testgen import text

FIXED = [[], ["one"], ["a", "b", "c"], ["mississippi", "pins"], ["hello world", "lower"],
         ["abc", "xyz"], ["", "abc"], ["abc", ""], ["aaa", "a"], ["a b", " "]]


def cases(rng):
    return FIXED + [[text(rng, 0, 30, "abcdefgh ,!"), text(rng, 0, 30, "abcdefgh ,!")]
                    for _ in range(30)]
