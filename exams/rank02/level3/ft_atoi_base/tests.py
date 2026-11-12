DIGITS = "0123456789abcdef"
FIXED = [("0", 10), ("42", 10), ("-42", 10), ("101010", 2), ("ff", 16), ("FF", 16),
         ("-7fffffff", 16), ("12fdb3", 16), ("12FDB3", 16), ("777", 8), ("zz", 16), ("", 10)]


def to_base(n, base, rng):
    if n == 0:
        return "0"
    out = ""
    while n:
        d = DIGITS[n % base]
        out = (d.upper() if rng.random() < 0.5 else d) + out
        n //= base
    return out


def cases(rng):
    pairs = list(FIXED)
    for _ in range(40):
        base = rng.randint(2, 16)
        n = rng.randint(0, 2147483647)
        pairs.append((("-" if rng.random() < 0.3 else "") + to_base(n, base, rng), base))
    return [{"args": [s, str(b)], "label": f"ft_atoi_base({s!r}, {b})"} for s, b in pairs]
