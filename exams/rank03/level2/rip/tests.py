FIXED = ["())", "(()()", "(())", ")(", "(", ")", "()", "((((", "))))", "()())()",
         "(()(()(", "((()()())())"]


def cases(rng):
    words = list(FIXED) + ["".join(rng.choice("()") for _ in range(rng.randint(1, 16)))
                           for _ in range(25)]
    return [[w] for w in words]
