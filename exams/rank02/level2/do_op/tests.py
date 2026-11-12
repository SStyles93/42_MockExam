FIXED = [
    [], ["1", "+"], ["1", "+", "2", "3"],
    ["21", "*", "2"], ["-17", "%", "5"], ["7", "/", "-2"], ["0", "-", "0"],
    ["2147483647", "-", "1"], ["-2147483647", "+", "-1"], ["5", "%", "7"],
]


def cases(rng):
    out = list(FIXED)
    for _ in range(40):
        op = rng.choice("+-*/%")
        if op == "*":
            a, b = rng.randint(-40000, 40000), rng.randint(-40000, 40000)
        else:
            a, b = rng.randint(-10**9, 10**9), rng.randint(-10**9, 10**9)
        if op in "/%" and b == 0:
            b = 3
        out.append([str(a), op, str(b)])
    return out
