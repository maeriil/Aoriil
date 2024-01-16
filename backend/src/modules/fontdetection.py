"""
This module, fontdetection, contains functionalities to determine the font size
of the original text in the image.

TODO This module contains many similarities between textinsertion module
Revamp this module so we dont rewrite same variables/functions

TODO This module does not work as intended. It does not calculate the original
font size properly and the calculated size is not even remotely close. Figure
out the issue and revamp this codebase. Priority is high

"""

import math
import textwrap
from PIL import ImageFont

# TODO: Should Wild Words be the default font type? The default fond type
# should be aggreable.
DEFAULT_FONT_NAME = "wild-words"


# TODO: We want to specify paths to font file outside of this file, in a
# different location. This is an low priority enhancement
DEFAULT_FONT_PATH = "src/utilities/fonts/Wild-Words-Roman.ttf"


# TODO: What should be the default font size used on most mangas? Is 12
# font size aggreable?
DEFAULT_FONT_SIZE = 12


DEFAULT_FONT_COLOR = "#000"


# TODO: What should be the smallest font size used on most mangas? Is 10
# font size aggreable?
MINIMUM_FONT_SIZE = 10


# TODO: What should be the largest font size used on most mangas? Is 30
# font size aggreable?
MAXIMUM_FONT_SIZE = 30


MIN_IMG_SPACE_THRESHOLD = 5


# TODO: This function is already implemented in textinsertion. Remove from here
def get_text_dimensions(
    text_string: str, font: ImageFont.ImageFont
) -> (int, int):
    """
    Determines the total length of the text and total height of text based
    of the font provided

    Parameters
    ----------
    text_string : str
        The string to determine width and height of

    font : ImageFont.ImageFont
        The font of the string to find width and height of

    Returns
    -------
    int
        The width of the string based on provided font

    int
        The height of the string based on provided font
    """

    _, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return text_width, text_height


def calculate_font_size(
    src_text,
    start_pos,
    end_pos,
    font_name=DEFAULT_FONT_NAME,
    scale=1,
):
    """
    Determine the font size of the provided text in the bounding box

    Parameters
    ----------
    src_text : str
        The text string's font size to determine

    start_pos : list
        The starting position point of the bounding box in original image

    end_pos : list
        The ending position point of the bounding box in original image

    font_name : str, optional
        The name of the font in the source text

    scale : int, optional
        The integer value to scale all text contents dimensions in image

    Returns
    -------
    int
        The calculated font size of the text given the bounding box dimensions
    """

    image_width = abs(end_pos[0] - start_pos[0])
    image_height = abs(end_pos[1] - start_pos[1])

    # line_height_gap = interpolate()
    padding = 3

    font_path = DEFAULT_FONT_PATH

    if font_name == "wild-words":
        font_path = "src/utilities/fonts/Wild-Words-Roman.ttf"

    left = MINIMUM_FONT_SIZE * scale
    right = MAXIMUM_FONT_SIZE * scale

    def calc_total_text_height(size) -> int:
        font_type = ImageFont.truetype(font_path, size)
        text_width, text_height = get_text_dimensions(src_text, font_type)
        text_width = math.floor((image_width - padding * 2) / text_width)
        if text_width <= 0:
            return -1

        content = textwrap.wrap(
            src_text, width=text_width, break_long_words=False
        )
        num_of_lines = len(content)
        total_height = num_of_lines * text_height + (padding * 2)
        return total_height

    def is_font_size_small(curr_font_size: int) -> bool:
        total_height = calc_total_text_height(curr_font_size)

        if (
            image_height >= total_height
            and image_height <= total_height + MIN_IMG_SPACE_THRESHOLD
        ):
            return False
        elif total_height == -1:
            return False
        else:
            return True

    def is_font_size_big(curr_font_size: int) -> bool:
        total_height = calc_total_text_height(curr_font_size)

        if total_height == -1:
            return True

        return total_height >= image_height

    while left <= right:
        mid_font_size = math.floor((left + right) / 2)
        if is_font_size_small(mid_font_size):
            left = mid_font_size + 1
        elif is_font_size_big(mid_font_size):
            right = mid_font_size - 1
        else:
            return mid_font_size

    return mid_font_size
