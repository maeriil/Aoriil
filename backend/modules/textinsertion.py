from PIL import Image, ImageFont, ImageDraw

import math
import numpy as np
import textwrap

"""

"""

MINIMUM_FONT_SIZE = 10
MAXIMUM_FONT_SIZE = 30
MAXIMUM_PIXELS_FOR_OVERFLOW = 24
MINIMUM_LINE_HEIGHT = 0.5

LINE_HEIGHT_INCREMENT_AMOUNT = 0.1
LINE_HEIGHT_DEFAULT_VAL = 1.3

IMAGE_ROTATE_DEG = 90
IMAGE_REVERSE_ROTATE_DEG = 270

DEFAULT_IMAGE_HEIGHT = 1000  # assume default imgs have 1000 pixels in height
LOWEST_SCALE_VAL = 1


def needs_vertical_text(box_width, box_height):
    ratio = box_width / box_height

    if ratio <= 0.2:
        return True
    return False


def get_text_dimensions(
    text_string: str, font: ImageFont.FreeTypeFont
) -> list:
    """"""
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return [text_width, text_height]


def get_overflow_amount(
    text: str,
    box_width: int,
    box_height: int,
    font_size: int,
    font_path: str,
    padding: int,
    line_height: int,
) -> (int, int):
    """"""
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
    """"""
    overflow_width, overflow_height = get_overflow_amount(
        text, box_width, box_height, font_size, font_path, padding, line_height
    )
    return overflow_width > 0 or overflow_height > 0


def too_much_overflow(
    text, box_width, box_height, font_size, font_path, padding, line_height
):
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


def manage_text(
    image: Image.Image,
    text: str,
    start_pos: list,
    box_width: int,
    box_height: int,
    font_size: int = 12,
    font_path: str = "utilities/fonts/Wild-Words-Roman.ttf",
    padding: int = 2,
    line_height: int = 1,
    vertical_text: bool = False,
    stroke_width=3,
) -> Image.Image:
    """"""
    scale = max(
        math.floor(image.height / DEFAULT_IMAGE_HEIGHT), LOWEST_SCALE_VAL
    )

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
        print("image width, height is ", image.width, image.height)
        print("start_x, start_y is ", start_x, start_y)
        print("box width, height = ", box_width, box_height)
        start_pos = [(image.width - (start_y + box_width)), start_x]
        print("finalized start pos is ", start_pos)

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
    )


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
