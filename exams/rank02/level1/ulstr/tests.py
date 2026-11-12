from engine.testgen import sentence, text

FIXED = [[], ["two", "args"], [""], ["   "], ["\t \t"], ['@[`{ edges of the letter ranges'], ['ALL CAPS'], ['all lower']]


def cases(rng):
    return (FIXED
            + [[sentence(rng)] for _ in range(30)]
            + [[text(rng)] for _ in range(10)])
