import cv2
import numpy as np
import textwrap


def sharpen_image(image: np.array) -> np.array:
    """ """
    pass


def binarize_image(image: np.array) -> np.array:
    """ """
    pass


def inlarge_image(image: np.array, configs: list) -> np.array:
    """ """
    pass


def shrink_image(image: np.array, configs: list) -> np.array:
    """ """
    pass


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


def draw_text(box: tuple, translated_text: str) -> np.array:
    """ """
    (top_left, top_right, bottom_right, bottom_left) = box
    (img_width, img_height) = (
        int(top_right[0] - top_left[0]),
        int(bottom_right[1] - top_right[1]),
    )
    text_image = np.full(
        (img_height, img_width, 3), 255, np.uint8
    )  # white img

    text = " ".join(translated_text.strip().split()).replace("\n", ". ")
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    font_color = (0, 0, 0)  # Black color in BGR
    thickness = 1
    max_width = img_width
    print("maximum width is ", max_width)

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
