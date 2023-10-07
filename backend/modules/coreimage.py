import utilities.helpers.imageHelpers as imgutil
import utilities.helpers.stringHelpers as strutil

import cv2
import numpy as np
import textwrap
import math

from PIL import Image, ImageFont, ImageDraw


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
    string: str, width: int, height: int, font_type
) -> (bool, bool):
    """"""
    MAXIMUM_WIDTH_MULTIPLIER = 2
    longest_word = strutil.get_longest_word_in_string(string)
    text_width, text_height = get_text_dimensions(longest_word, font_type)

    if text_width > width * MAXIMUM_WIDTH_MULTIPLIER and height > width:
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


def insert_text(translated_text, image, box):
    # convert the provided image to PIL image
    conv_image_color = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(conv_image_color)

    image_width = imgutil.calculate_box_width(box)
    image_height = imgutil.calculate_box_height(box)
    top_left, _, _, _ = imgutil.unpack_box(box)

    image_pil = insert_text_to_pil_img(
        translated_text, image_pil, image_width, image_height, top_left
    )

    return np.asarray(image_pil)


def insert_text_to_pil_img(
    translated_text, image, image_width, image_height, start_point, padding=2
):
    # image_width = image.width
    # image_height = image.height

    # TODO: we need to export the following default properties outside of
    # this file so we can change it/add more later accordingly
    (x, y) = start_point
    font_size = 12
    font_type = "utilities/fonts/Wild-Words-Roman.ttf"
    font_color = "#000"
    font_thickness = 1

    print(f"x is {x}, y is {y}")

    # first make sure the translated_text doesnt have unnecessary new lines
    translated_text = strutil.remove_trailing_whitespace(translated_text)
    text_font = ImageFont.truetype(font_type, font_size)
    is_vertical_layout_needed, remove_padding = needs_vertical_layout(
        translated_text, image_width, image_height, text_font
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
        )
        image = new_rotated_image.rotate(270, expand=True)
    else:
        drawing_img = ImageDraw.Draw(image)

        if remove_padding:
            padding = 0

        text_width, text_height = get_text_dimensions("W", text_font)

        text_width = math.floor((image_width - padding * 2) / text_width)
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


# converting image to PIL's Image format so we can use custom font
# then revert it back to cv2 image format
# @deprecated
def draw_text(box: tuple, translated_text: str, text_image) -> np.array:
    """ """
    (top_left, top_right, bottom_right, bottom_left) = box
    (img_width, img_height) = (
        int(top_right[0] - top_left[0]),
        int(bottom_right[1] - top_right[1]),
    )
    # text_image = np.full(
    #     (img_height, img_width, 3), 255, np.uint8
    # )  # white img

    text = " ".join(translated_text.strip().split()).replace("\n", ". ")
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    font_color = (0, 0, 0)  # Black color in BGR
    thickness = 1
    max_width = img_width
    lines = []
    words = text.split()
    while words:
        line = words.pop(0)
        while (
            words
            and cv2.getTextSize(
                line + " " + words[0], font, font_scale, thickness
            )[0][0]
            < max_width
        ):
            line += " " + words.pop(0)
        lines.append(line)
    wrapped_lines = lines

    total_text_height = len(wrapped_lines) * int(
        cv2.getTextSize(text, font, font_scale, thickness)[0][1]
    )

    # Calculate the starting y-coordinate to vertically center the wrapped text
    start_y = (text_image.shape[0] - total_text_height) // 2

    # Display the wrapped text on the image
    for line in wrapped_lines:
        text_width = cv2.getTextSize(line, font, font_scale, thickness)[0][0]
        start_x = (text_image.shape[1] - text_width) // 2
        cv2.putText(
            text_image,
            line,
            (start_x, start_y),
            font,
            font_scale,
            font_color,
            thickness,
        )
        start_y += int(
            cv2.getTextSize(line, font, font_scale, thickness)[0][1]
        )

    return text_image


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
