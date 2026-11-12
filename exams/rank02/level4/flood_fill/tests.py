FIXED = [
    (2, 1, ["1100", "1000", "0011"]),
    (0, 0, ["0"]),
    (0, 0, ["11111", "10001", "10101", "10001", "11111"]),
    (2, 2, ["11111", "10001", "10101", "10001", "11111"]),
    (1, 1, ["101", "010", "101"]),
    (4, 0, ["0000000000"]),
    (0, 3, ["1", "1", "1", "1"]),
]


def cases(rng):
    grids = list(FIXED)
    for _ in range(30):
        w, h = rng.randint(1, 25), rng.randint(1, 15)
        chars = rng.choice(["01", "012", "0011", "ab"])
        rows = ["".join(rng.choice(chars) for _ in range(w)) for _ in range(h)]
        grids.append((rng.randrange(w), rng.randrange(h), rows))
    return [{"args": [str(x), str(y)] + rows,
             "label": f"flood_fill(begin={{{x}, {y}}}) on " + "/".join(rows)}
            for x, y, rows in grids]
