FIXED = [["6", "1", "2", "3", "4", "5"], ["0", "3", "-3"], ["100", "1", "2", "3"], ["0"],
         ["5"], ["7", "7"], ["0", "0"], ["3", "1", "0", "2", "4", "5", "3"]]


def cases(rng):
    out = list(FIXED)
    for _ in range(20):
        size = rng.randint(1, 16)
        pool = rng.sample(range(-20, 40), size)
        if rng.random() < 0.7:
            target = sum(x for x in pool if rng.random() < 0.4)
        else:
            target = rng.randint(-30, 60)
        out.append([str(target)] + [str(x) for x in pool])
    return out
