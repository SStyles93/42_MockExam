FIXED = ["1, 1\n0, 1\n1, 0\n0, 0\n", "0, 0\n1, 0\n2, 0\n0, 1\n1, 1\n2, 1\n", "5, 5\n",
         "0, 0\n3, 4\n", "0, 0\n10, 0\n10, 10\n0, 10\n5, 5\n",
         "0, 0\n1, 0\n2, 0\n0, 1\n1, 1\n2, 1\n1, 2\n2, 2\n"]


def cases(rng):
    inputs = list(FIXED)
    for _ in range(14):
        n = rng.randint(2, 10)
        pts = [(round(rng.uniform(-50, 50), 2), round(rng.uniform(-50, 50), 2))
               for _ in range(n)]
        inputs.append("".join(f"{x}, {y}\n" for x, y in pts))
    return [{"args": [], "stdin": s, "label": f"./tsp < ({s.count(chr(10))} cities)"}
            for s in inputs]
