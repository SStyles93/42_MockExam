def cases(rng):
    chunks = [list(range(i, i + 8)) for i in range(0, 256, 8)]
    return [{"args": [str(n) for n in c], "label": f"reverse_bits(n) for n in {c[0]}..{c[-1]}"}
            for c in chunks]
