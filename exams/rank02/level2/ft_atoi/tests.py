FIXED = ["0", "42", "-42", "+42", "   \t\n\v\f\r 123", "2147483647", "-2147483647",
         "--5", "+-5", "-+5", "12abc34", "abc", "", " - 5", "007", "  +0", "99 bottles"]


def cases(rng):
    strings = list(FIXED)
    for _ in range(30):
        n = rng.randint(-2147483647, 2147483647)
        prefix = "".join(rng.choice(" \t\n\v\f\r") for _ in range(rng.randint(0, 3)))
        sign = "+" if n >= 0 and rng.random() < 0.3 else ""
        suffix = rng.choice(["", "", "x", " 12", "-3", "."])
        strings.append(f"{prefix}{sign}{n}{suffix}")
    return [{"args": [s], "label": f"ft_atoi({s!r})"} for s in strings]
