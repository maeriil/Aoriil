import utilities.helpers.imageHelpers as imgutil
import utilities.helpers.stringHelpers as strutil

import cv2
import numpy as np
import textwrap
import math

from PIL import Image, ImageFont, ImageDraw


def calc_max_gap_dist(image: np.array) -> int:
    height, width, channel = image.shape
    return math.floor((7.5 * height) / 1000)


def sharpen_image(image: np.array) -> np.array:
    """ """
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Add blur to the image
    # extract the gaussian kernal to global scope and make it a constant
    image = cv2.GaussianBlur(image, (9, 9), 0)

    # use threshold to do TODO: WHAT?
    image = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Attempt to remove noise from the image
    # extract the kernal matrix to global scope and make it a constant
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # What does this do? TODO
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)

    # Invert the image colours
    # image = 255 - image

    return image


def temp_test(im):
    # smooth the image with alternative closing and opening
    # with an enlarging kernel
    morph = im.copy()

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    morph = cv2.morphologyEx(morph, cv2.MORPH_CLOSE, kernel)
    morph = cv2.morphologyEx(morph, cv2.MORPH_OPEN, kernel)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))

    # take morphological gradient
    # gradient_image = cv2.morphologyEx(morph, cv2.MORPH_GRADIENT, kernel)
    gradient_image = morph

    # split the gradient image into channels
    image_channels = np.split(np.asarray(gradient_image), 3, axis=2)

    channel_height, channel_width, _ = image_channels[0].shape

    # apply Otsu threshold to each channel
    for i in range(0, 3):
        _, image_channels[i] = cv2.threshold(
            ~image_channels[i], 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY
        )
        image_channels[i] = np.reshape(
            image_channels[i], newshape=(channel_height, channel_width, 1)
        )

    # merge the channels
    image_channels = np.concatenate(
        (image_channels[0], image_channels[1], image_channels[2]), axis=2
    )
    return image_channels


def binarize_image(image: np.array) -> np.array:
    """ """
    pass


def inlarge_image(image: np.array, configs: list) -> np.array:
    """ """
    pass


def shrink_image(image: np.array, configs: list) -> np.array:
    """ """
    pass


def morph_close(image: np.array, kernal_size: int = 5) -> np.array:
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (kernal_size, kernal_size)
    )
    processed_img = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)

    return processed_img


def morph_dilate(image: np.array, kernal_size: int = 5) -> np.array:
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE, (kernal_size, kernal_size)
    )
    processed_img = cv2.morphologyEx(image, cv2.MORPH_DILATE, kernel)

    return processed_img


def crop_image(image, box: list):
    """ """
    (top_left, top_right, bottom_right, bottom_left) = box
    x1, y1, x2, y2 = (
        int(top_left[0]),
        int(top_left[1]),
        int(top_right[0]),
        int(bottom_left[1]),
    )

    cropped = image[y1:y2, x1:x2]

    return cropped


def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return [text_width, text_height]


def needs_vertical_layout(
    string: str, width: int, height: int, font_type, padding
) -> (bool, bool):
    """"""
    MAXIMUM_WIDTH_MULTIPLIER = 1.5
    longest_word = strutil.get_longest_word_in_string(string)
    text_width, text_height = get_text_dimensions(longest_word, font_type)

    text_width = math.floor((width - padding * 2) / text_width)
    content = textwrap.wrap(string, width=width, break_long_words=False)

    total_text_height = (text_height + padding) * len(content)
    y_offset = math.floor((height - total_text_height) / 2)

    if text_width > width * MAXIMUM_WIDTH_MULTIPLIER and height > width:
        print("first case Vertical Layout needed")
        return True, False
    if y_offset < 0 and height > width:
        print("main case? Vertical Layout needed")
        return True, False
    elif text_width > width and text_width <= width * MAXIMUM_WIDTH_MULTIPLIER:
        return False, True
    #  default_padding=2, 2*padding=4,
    # TODO: remove magic number and make it a constant somewhere
    elif text_width >= width and text_width - 4 <= width:
        return False, True
    else:
        return False, False


def calculate_width(string: str) -> int:
    return 15


def insert_text(translated_text, image, box, font_size) -> Image.Image:
    image_width = imgutil.calculate_box_width(box)
    image_height = imgutil.calculate_box_height(box)
    top_left, _, _, _ = imgutil.unpack_box(box)

    image = insert_text_to_pil_img(
        translated_text,
        image,
        image_width,
        image_height,
        top_left,
        font_size=font_size,
    )

    return image


def insert_text_to_pil_img(
    translated_text,
    image,
    image_width,
    image_height,
    start_point,
    font_size=12,
    padding=2,
) -> Image.Image:
    # TODO: we need to export the following default properties outside of
    # this file so we can change it/add more later accordingly
    print(f"dimensions are {image_width}x{image_height}")
    (x, y) = start_point
    font_type = "utilities/fonts/Wild-Words-Roman.ttf"
    font_color = "#000"
    font_thickness = 1

    print(f"x is {x}, y is {y}")

    # first make sure the translated_text doesnt have unnecessary new lines
    translated_text = strutil.remove_trailing_whitespace(translated_text)
    text_font = ImageFont.truetype(font_type, font_size)
    is_vertical_layout_needed, remove_padding = needs_vertical_layout(
        translated_text, image_width, image_height, text_font, padding=padding
    )

    # determine which layout we will save the text as
    # There are two ways we can save text, horizontally or vertically
    # By default we prefer to use horizontal layout. However, if our bounding
    # box is very tall but very small width, we will convert it to vertical
    # text. Each line will only contain a single character.

    # flip the image and call the same function
    if is_vertical_layout_needed:
        rotated_image = image.rotate(90, expand=True)
        new_rotated_image = insert_text_to_pil_img(
            translated_text,
            rotated_image,
            image_height,
            image_width,
            start_point,
            font_size=font_size,
        )
        image = new_rotated_image.rotate(270, expand=True)
    else:
        drawing_img = ImageDraw.Draw(image)

        if remove_padding:
            padding = 0

        text_width, text_height = get_text_dimensions("W", text_font)
        print(f"img width={image_width}, height={image_height}")
        print(f"text width={text_width}, height={text_height}")

        text_width = math.ceil((image_width - padding * 2) / text_width)
        print(f"updated text width={text_width}, height={text_height}")

        content = textwrap.wrap(
            translated_text, width=text_width, break_long_words=False
        )

        total_text_height = (text_height + padding) * len(content)
        y_offset = math.floor((image_height - total_text_height) / 2)
        print("y offset is ", y_offset)

        for line in content:
            text_box = drawing_img.textbbox((x, y), line, text_font)
            line_width, line_height = get_text_dimensions(line, text_font)

            # line_width = imgutil.calculate_width(text_box[2], text_box[0])
            # line_height = imgutil.calculate_height(text_box[3], text_box[1])

            x_offset = math.floor((image_width - line_width - padding * 2) / 2)

            drawing_img.text(
                (x + x_offset, y + y_offset),
                line,
                font=text_font,
                fill="#000",
                stroke_width=2,
                stroke_fill="white",
            )
            y_offset += line_height + padding

    # convert back to cv2 image and return it
    return image


def replace_image_section(image, text_image, box):
    """ """
    (top_left, top_right, bottom_right, bottom_left) = box
    dimension = (top_right[0] - top_left[0], bottom_right[1] - top_right[1])
    (x_offset, y_offset) = top_left
    x_offset = int(x_offset)
    y_offset = int(y_offset)
    image[
        y_offset : y_offset + text_image.shape[0],
        x_offset : x_offset + text_image.shape[1],
    ] = text_image

    return image
