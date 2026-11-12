from engine.testgen import sentence, text

FIXED = [[], ["two", "args"], [""], ["   "], ["\t \t"], ['abcdefghijklmnopqrstuvwxyz'], ['ZzYy'], ['no letters? 123']]


def cases(rng):
    return (FIXED
            + [[sentence(rng)] for _ in range(30)]
            + [[text(rng)] for _ in range(10)])
