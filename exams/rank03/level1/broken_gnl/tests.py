from engine.testgen import text

FIXED = ["", "\n", "no newline at the end", "one line\n", "\n\n\n", "a\nbb\nccc\n",
         "a\nbb\nccc", "x" * 10000 + "\nend", "  spaces  \n\ttabs\t\n"]


def random_text(rng):
    lines = [text(rng, 0, rng.choice([5, 50, 300])) for _ in range(rng.randint(1, 30))]
    out = "\n".join(lines)
    return out + "\n" if rng.random() < 0.5 else out


def cases(rng):
    inputs = FIXED + [random_text(rng) for _ in range(15)]
    return [{"args": [], "stdin": s, "label": f"get_next_line(0) until NULL, input of "
             f"{len(s)} bytes / {s.count(chr(10))} newline(s)"} for s in inputs]
