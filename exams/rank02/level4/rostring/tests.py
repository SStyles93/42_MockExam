from engine.testgen import sentence

FIXED = [[], ["one two three"], ["   spaced    out   words "], ["solo   "], ["first", "ignored"],
         [""], ["  \t "], ["\ttab\tseparated\t"]]


def cases(rng):
    return FIXED + [[sentence(rng)] for _ in range(30)]
