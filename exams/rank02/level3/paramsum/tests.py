def cases(rng):
    out = [[], ["a"], [""], ["a", "b", "c"], ["one argument with spaces"], ["x"] * 100]
    out += [[str(i) for i in range(rng.randint(0, 50))] for _ in range(10)]
    return out
