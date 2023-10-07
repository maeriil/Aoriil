def remove_trailing_whitespace(string: str) -> str:
    """"""
    return " ".join(string.strip().split()).replace("\n", "")


def covert_to_vertical_text(string: str) -> str:
    """"""
    pass


def get_longest_word_in_string(string: str) -> str:
    """"""
    words = string.split()
    return max(words, key=len)
