WORDS = ["get", "next", "line", "is", "a", "camel", "x", "value", "of", "html", "parser", "b"]


def camel(rng):
    words = [rng.choice(WORDS) for _ in range(rng.randint(1, 6))]
    return words[0] + "".join(w.capitalize() for w in words[1:])


def snake(rng):
    return "_".join(rng.choice(WORDS) for _ in range(rng.randint(1, 6)))


FIXED = [[], ["a", "b"], [""], ["x"], ["getNextLine"], ["isAValidInput"], ["htmlParser"]]


def cases(rng):
    return FIXED + [[camel(rng)] for _ in range(30)]
