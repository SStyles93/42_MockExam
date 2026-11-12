from engine.testgen import text

FIXED = [[], ["one"], ["a", "b", "c"], ["banana", "apple"], ["abc", "cba"], ["", "zz top"],
         ["", ""], ["aaa", "aaa"]]


def cases(rng):
    return FIXED + [[text(rng, 0, 30, "abcdefgh ,!"), text(rng, 0, 30, "abcdefgh ,!")]
                    for _ in range(30)]
