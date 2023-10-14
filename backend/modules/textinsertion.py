"""
This module, textinsertion, contains functionalities to insert translated text
into the provided image. Note that all the images in this section will be using
Pillow image in order to use custom ImageFont and easier writing methods. 

"""

import math
import numpy as np
import textwrap

from PIL import Image, ImageFont, ImageDraw


# TODO: Need to agree upon MINIMUM and MAXMIMUM font sizes for most mangas
MINIMUM_FONT_SIZE = 10
MAXIMUM_FONT_SIZE = 30


# TODO: How much text overflow from the bounding box is fine? How can we
# better determine this? Currently, using Wild Words font, we see that
# a size 13 character is approxmiately 12 pixels long in images with
# 1000 pixel as height. The value 24 is set to allow 2 such characters.
# Find a better way to deal with "allowed text overflow"
MAXIMUM_PIXELS_FOR_OVERFLOW = 24


# TODO: If the translated text is too big and the bounding box is too small
# how much line height can we shrink it down to until the texts fit inside
# the bounding box. Is it even readable when line height is at the specified
# minimum amount? Testing is needed
MINIMUM_LINE_HEIGHT = 0.5

LINE_HEIGHT_INCREMENT_AMOUNT = 0.1


# TODO: What is the most optimal line height such that the text doesnt seem too
# squished? Currently its set to 1 but agree on if this makes sense or not
LINE_HEIGHT_DEFAULT_VAL = 1

IMAGE_ROTATE_DEG = 90
IMAGE_REVERSE_ROTATE_DEG = 270

DEFAULT_IMAGE_HEIGHT = 1000  # assume default imgs have 1000 pixels in height
DEFAULT_IMAGE_WIDTH = 1000
LOWEST_SCALE_VAL = 1


# TODO: Currently, the 0.2 ratio is hardcoded. We want to not determine if
# we need to print text vertically like this. Figure out a way to fix this
# TODO: Check for division by zero potentially
def needs_vertical_text(box_width: int, box_height: int) -> bool:
    """
    Determine if we need to set the text in rotated format based on the
    dimensions of the box.

    Parameters
    ----------
    box_width : int
        The width of the box

    box_height : int
        The height of the box

    Returns
    -------
    bool
        True if we need vertical text, False otherwise
    """

    ratio = box_width / box_height

    if ratio <= 0.2:
        return True
    return False


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


# TODO: Currently we are using the fact that the character 'W' is the widest
# english character to get the size of characer in pixel. This is because the
# width in textwrap module's wrap takes width as CHARACTERS, NOT PIXELS.
# So we need to divide box_width by a single character pixel to determine
# how much letters we can fit in the bounding box. Determine if this is the
# best way to do this calculation or not...
def get_overflow_amount(
    text: str,
    box_width: int,
    box_height: int,
    font_size: int,
    font_path: str,
    padding: int,
    line_height: int,
) -> (int, int):
    """
    Determines how much the texts will overflow by, by comparing the longest
    sentence in the strings list after it has been word wrapped

    Parameters
    ----------
    text : str
        The text content to determine how much it will overflow by

    box_width : int
        The bounding box's width that it will be comparing to

    box_height : int
        The bounding box's height that it will be comparing to

    font_size : int
        The font size used to determine the overflow amount

    font_path : str
        The path to the custom font file

    padding : int
        The amount of padding added to left and right side of each line

    line_height : int
        The amount of vertical spacing between each lines

    Returns
    -------
    int
        How much the text will overflow horizontally comparing to the bounding
        box
    int
        How much the text will overflow vertically comparing to the bounding
        box
    """

    # creates font with certain size
    font = ImageFont.truetype(font_path, font_size)

    # W is the widest english character
    char_width, char_height = get_text_dimensions("W", font)
    number_of_allowed_char = math.ceil((box_width - padding * 2) / char_width)
    contents = textwrap.wrap(
        text, width=number_of_allowed_char, break_long_words=False
    )

    longest_sentence = max(contents, key=len)
    longest_sentence_width = len(longest_sentence) * char_width
    text_wrapped_lines_height = (len(contents) * char_height) + (
        (len(contents) - 1) * line_height
    )

    overflow_width = (longest_sentence_width + padding * 2) - box_width
    overflow_height = (text_wrapped_lines_height + padding * 2) - box_height

    return overflow_width, overflow_height


def overflow(
    text, box_width, box_height, font_size, font_path, padding, line_height
):
    """
    Determines if the texts will overflow or not

    Parameters
    ----------
    text : str
        The text content to determine how much it will overflow by

    box_width : int
        The bounding box's width that it will be comparing to

    box_height : int
        The bounding box's height that it will be comparing to

    font_size : int
        The font size used to determine the overflow amount

    font_path : str
        The path to the custom font file

    padding : int
        The amount of padding added to left and right side of each line

    line_height : int
        The amount of vertical spacing between each lines

    Returns
    -------
    bool
        True if text overflowed either horizontally or vertically,
        False otherwise
    """

    overflow_width, overflow_height = get_overflow_amount(
        text, box_width, box_height, font_size, font_path, padding, line_height
    )

    return overflow_width > 0 or overflow_height > 0


# TODO: What is "too" much overflow. What is a "passable" overflow?
# Currently we determine it like this. If we are overflowing out of bounding
# box vertically, then we consider it as a "bad overflow".
# If we overflow horizontally out of bounding box, and if the overflow amount
# is not too much, then it is "passable". This is because we dont detect the
# text bubble, but rather the text itself. Hence on most cases, there will
# already be a lot of extra spaces outside of the bounding box, more often
# horizontally. So it is okay to overflow a little horizontally
# But is this really a good idea? And how can we better improve this? One way
# is to detect the Bubbles itself rather than detecting texts...
def too_much_overflow(
    text, box_width, box_height, font_size, font_path, padding, line_height
):
    """
    Determines if the texts will overflow or not

    Parameters
    ----------
    text : str
        The text content to determine how much it will overflow by

    box_width : int
        The bounding box's width that it will be comparing to

    box_height : int
        The bounding box's height that it will be comparing to

    font_size : int
        The font size used to determine the overflow amount

    font_path : str
        The path to the custom font file

    padding : int
        The amount of padding added to left and right side of each line

    line_height : int
        The amount of vertical spacing between each lines

    Returns
    -------
    bool
        True if text overflowed vertically.
        True if text overflowed more than specified horizontal threshold.
        False otherwise
    """

    overflow_width, overflow_height = get_overflow_amount(
        text, box_width, box_height, font_size, font_path, padding, line_height
    )

    # if we overflowed vertically, then its no good
    if overflow_height > 0:
        return True

    # if we increased the maximum pixels allowed for overflowing, then no good
    if overflow_width > MAXIMUM_PIXELS_FOR_OVERFLOW * 2:
        return True
    return False


# TODO: Currently we are passing the font path to this function manually.
# we are also setting the default value of the font_path manually as well
# We do not want to do it like this because if we changed the path to fonts,
# we dont want this function to suddenly break...
# TODO: The default font_size is set to 12. Is this the agreed font size for
# most bubbles? We will need to agree all on it
# TODO: stroke_width refers to the white background we add to each letter. This
# is needed because we want the font colour to be black by default but we also
# want to see the text if the background is black. But what is a good value to
# have as a text stroke? We will need to agree on this
# TODO: How do we better "scale" texts when the images are of higher/lower
# dimensions? How do we ensure the text is always readable? Will need to work
# more on this
# TODO: Currently, the fontdetection module is not calculating font sizes
# correctly. Because of this, the passed original text's fontsize, font_size,
# is incorrect. In order to temporarily fix this, We have added a check to
# return font_size = 15, if passed font_size was between 10 and 20.
# We do NOT want to calculate font size like this. Urgent fix needed
def manage_text(
    image: Image.Image,
    text: str,
    start_pos: list,
    box_width: int,
    box_height: int,
    font_size: int = 12,
    font_path: str = "utilities/fonts/Wild-Words-Roman.ttf",
    padding: int = 2,
    line_height: int = LINE_HEIGHT_DEFAULT_VAL,
    vertical_text: bool = False,
    stroke_width=3,
    stroke_color="white",
) -> Image.Image:
    """
    Wrapper for inserting text to the image. Does multiple sanity checks
    to ensure that the text will fit perfectly into the boundind boxes.

    Parameters
    ----------
    image : Image.Image
        The image to write the text content to

    text : str
        The text contents to insert to the provided image

    start_pos : list
        The start position point in the image. It must be within the image's
        dimensions

    box_width : int
        The maximum width of the bounding box of the text.

    box_height : int
        The maxmimum height of the bounding box of the text

    font_size : int, optional
        The font size of the text. Default font size is set to 12 pixels

    font_path : str, optional
        The font path for the custom font. Default font is Wild Words Normal

    padding : int, optional
        Left, right, top, bottom paddings to add while displaying the text.
        Default padding amount is 2 pixels.

    line_height : int, optional
        Vertical line spacing between two lines of texts. Default value is 1px

    vertical_text : bool, optional
        Write the text vertically* if this is provided. Default value is False
        *Writing text vertically means display it rotated 90degrees

    stroke_width : int, optional
        The width of the stroke outlines on each character. Default is 3px

    stroke_color : str, optional
        The colour of the strokes to display on texts. Default is white color

    Returns
    -------
    Image.Image
        Pillow Image after the text has been added to it with specified props
    """

    height_scale = max(
        math.floor(image.height / DEFAULT_IMAGE_HEIGHT), LOWEST_SCALE_VAL
    )
    width_scale = max(
        math.floor(image.width / DEFAULT_IMAGE_WIDTH), LOWEST_SCALE_VAL
    )
    scale = min(width_scale, height_scale)

    # TODO: REMOVE THIS, THIS IS ONLY A BANDAID
    if font_size >= 10 and font_size <= 20:
        font_size = 15

    # if font size was somehow set below 10, reset to 10
    if font_size < MINIMUM_FONT_SIZE:
        font_size = MINIMUM_FONT_SIZE

    if needs_vertical_text(box_width, box_height):
        vertical_text = True
        start_x, start_y = start_pos[0], start_pos[1]
        image = image.rotate(IMAGE_REVERSE_ROTATE_DEG, expand=True)
        box_width, box_height = box_height, box_width
        start_pos = [(image.width - (start_y + box_width)), start_x]

    if overflow(
        text, box_width, box_height, font_size, font_path, padding, line_height
    ):
        while (
            too_much_overflow(
                text,
                box_width,
                box_height,
                font_size,
                font_path,
                padding,
                line_height,
            )
            and font_size > MINIMUM_FONT_SIZE
        ):
            font_size -= 1

    if font_size == MINIMUM_FONT_SIZE:
        while (
            too_much_overflow(
                text,
                box_width,
                box_height,
                font_size,
                font_path,
                padding,
                line_height,
            )
            and padding > 0
        ):
            padding -= 1

    if font_size == MINIMUM_FONT_SIZE and padding == 0:
        while (
            too_much_overflow(
                text,
                box_width,
                box_height,
                font_size,
                font_path,
                padding,
                line_height,
            )
            and line_height > MINIMUM_LINE_HEIGHT
        ):
            line_height -= LINE_HEIGHT_INCREMENT_AMOUNT

    # if it still overflows here, then do nothing since we have tried enough
    # to fit it in.
    font_size *= scale
    padding *= scale
    line_height *= scale
    stroke_width *= scale

    font = ImageFont.truetype(font_path, font_size)

    return insert_text(
        image=image,
        text=text,
        start_pos=start_pos,
        box_width=box_width,
        box_height=box_height,
        font=font,
        padding=padding,
        line_height=line_height,
        vertical_text=vertical_text,
        background_stroke_width=stroke_width,
        background_stroke_color=stroke_color,
    )


# TODO: Needs error handling for this function. For example: If the new
# calcd starting position of the text turns out it is outside the image's
# dimension, we should throw an error and not paint it.
def insert_text(
    image: Image.Image,
    text: str,
    start_pos: list,
    box_width: int,
    box_height: int,
    font: ImageFont.ImageFont,
    font_color: str = "#000",
    padding: int = 12,
    line_height: int = LINE_HEIGHT_DEFAULT_VAL,
    vertical_text: bool = False,
    background_stroke_width: int = 3,
    background_stroke_color: str = "white",
) -> Image.Image:
    """
    Insert the provided text into the image based on given properties.

    Parameters
    ----------
    image : Image.Image
        The image to write the text content to

    text : str
        The text contents to insert to the provided image

    start_pos : list
        The start position point in the image. It must be within the image's
        dimensions

    box_width : int
        The maximum width of the bounding box of the text.

    box_height : int
        The maxmimum height of the bounding box of the text

    font : ImageFont.ImageFont
        The font which will be used to print the text to image

    font_color : str, optional
        The font color which will be used to print the text to image.
        Default font color is always black (#000)

    padding : int, optional
        Left, right, top, bottom paddings to add while displaying the text.
        Default padding amount is 2 pixels.

    line_height : int, optional
        Vertical line spacing between two lines of texts. Default value is 1px

    vertical_text : bool, optional
        Write the text vertically* if this is provided. Default value is False
        *Writing text vertically means display it rotated 90degrees

    background_stroke_width : int, optional
        The width of the stroke outlines on each character. Default is 3px

    background_stroke_color : str, optional
        The colour of the strokes to display on texts. Default is white color

    Returns
    -------
    Image.Image
        Pillow Image after the text has been added to it with specified props
    """

    drawing = ImageDraw.Draw(image)
    text_width, text_height = get_text_dimensions("W", font)
    text_width = math.ceil((box_width - padding * 2) / text_width)

    contents = []

    # if we are supposed to vertical text layout, just dont word wrap
    if vertical_text:
        contents = [text]
    else:
        contents = textwrap.wrap(
            text, width=text_width, break_long_words=False
        )

    contents_height = (text_height * len(contents)) + (
        line_height * (len(contents) - 1)
    )
    x_offset = 0
    y_offset = math.floor((box_height - contents_height - padding * 2) / 2)

    for line in contents:
        curr_line_width, _ = get_text_dimensions(line, font)
        x_offset = math.floor((box_width - curr_line_width - padding * 2) / 2)

        # TODO:
        # what if x_offset + start_pos[0] is somehow < start_pos in the img?
        # we need to build error handling for this
        # similar for y_offset + start_pos[1] as well

        drawing.text(
            (start_pos[0] + x_offset, start_pos[1] + y_offset),
            line,
            font=font,
            fill=font_color,
            stroke_width=background_stroke_width,
            stroke_fill=background_stroke_color,
        )

        y_offset += line_height + text_height

    if vertical_text:
        image = image.rotate(IMAGE_ROTATE_DEG, expand=True)

    return image
