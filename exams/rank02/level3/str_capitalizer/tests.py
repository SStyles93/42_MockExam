from engine.testgen import sentence

FIXED = [[], [""], ["a"], ["a FiRSt LiTTlE TESt"], ["  lead and trail  "], ["x Y z"],
         ["__under_scores and 42numbers"], ["one", "two args", "THREE ARGS HERE"],
         ["tab\tseparated\twords"], ["ends with dot."]]


def cases(rng):
    alpha = "abcdefghABCDEFGH0123_.,!"
    out = list(FIXED)
    for _ in range(30):
        out.append([sentence(rng, alphabet=alpha) for _ in range(rng.randint(1, 3))])
    return out
