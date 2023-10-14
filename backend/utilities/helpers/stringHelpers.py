"""
This module, stringHelpers, contains useful functions related to string
processing and other general stuff

If there is a string function used by at least two other functions, consider
placing the function here to follow D.R.Y Principles

"""


def remove_trailing_whitespace(string: str) -> str:
    """
    Remove all trailing whitespaces from the string including new lines

    Parameters
    ----------
    string : str
        The string to remove all trailing spaces from

    Returns
    -------
    str
        The formatted string
    """

    return " ".join(string.strip().split()).replace("\n", "")
