FIXED = [[], ["1", "2"], ["0"], ["-7"], ["1"], ["2"], ["3"], ["5"], ["7"], ["10"], ["100"],
         ["97"], ["1000"]]


def cases(rng):
    return FIXED + [[str(rng.randint(1, 50000))] for _ in range(20)]
