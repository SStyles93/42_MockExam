# Values stay moderate: the subject does not require an efficient algorithm.
FIXED = [[], ["42"], ["1", "2", "3"], ["48", "36"], ["17", "5"], ["100", "100"], ["1", "1"],
         ["999983", "1"], ["1", "999983"], ["1071", "462"]]


def cases(rng):
    out = list(FIXED)
    for _ in range(25):
        g = rng.randint(1, 1000)
        out.append([str(g * rng.randint(1, 1000)), str(g * rng.randint(1, 1000))])
    return out
