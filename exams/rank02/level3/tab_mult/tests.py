FIXED = [[], ["1"], ["7"], ["9"], ["10"], ["42"], ["238609294"]]


def cases(rng):
    return FIXED + [[str(rng.randint(1, 238609294))] for _ in range(15)]
