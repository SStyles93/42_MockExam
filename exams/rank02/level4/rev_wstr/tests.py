from engine.testgen import simple_sentence

FIXED = [[], ["a", "b"], ["alone"], ["the last shall be first"], ["a b"]]


def cases(rng):
    return FIXED + [[simple_sentence(rng, max_words=10)] for _ in range(30)]
