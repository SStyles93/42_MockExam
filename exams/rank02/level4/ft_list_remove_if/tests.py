FIXED = [["a"], ["a", "a"], ["a", "b"], ["a", "a", "b", "a"], ["x", "a", "b", "c"],
         ["b", "a", "b", "c"], ["a", "a", "a", "a"], ["", "", "x", ""]]


def cases(rng):
    out = list(FIXED)
    for _ in range(25):
        elems = [rng.choice("abcd") for _ in range(rng.randint(0, 20))]
        out.append([rng.choice("abcd")] + elems)
    return [{"args": c, "label": f"remove {c[0]!r} from {c[1:]}"} for c in out]
