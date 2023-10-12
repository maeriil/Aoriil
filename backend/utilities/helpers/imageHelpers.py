import cv2
import numpy as np

from functools import singledispatch
from PIL import Image


def convert_cv2_to_pil(image: np.array) -> Image.Image:
    conv_image_color = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(conv_image_color)
    return image_pil


def convert_pil_to_cv2(image: Image.Image) -> np.array:
    return np.asarray(image)


def unpack_box(box: list) -> (list, list, list, list):
    """"""
    if box is None:
        raise ValueError("Did not provide a box to unpack")
    if len(box) != 4:
        raise ValueError("Inappropriate amount of values provided to box")

    (top_left, top_right, bottom_right, bottom_left) = box

    # each of them could be float64 format. We will round them to integer
    top_left = list(map(round, top_left))
    top_right = list(map(round, top_right))
    bottom_right = list(map(round, bottom_right))
    bottom_left = list(map(round, bottom_left))

    return top_left, top_right, bottom_right, bottom_left


def calculate_width(left_point_x: int, right_point_x: int) -> int:
    """"""
    return abs(left_point_x - right_point_x)


def calculate_box_width(box) -> int:
    """"""
    top_left, top_right, _, _ = unpack_box(box)

    return calculate_width(top_left[0], top_right[0])


def calculate_height(left_point_y: int, right_point_y: int) -> int:
    """"""
    return abs(left_point_y - right_point_y)


def calculate_box_height(box) -> int:
    """"""
    top_left, _, _, bottom_left = unpack_box(box)

    return calculate_height(top_left[1], bottom_left[1])


def crop_image(image: np.array, start_pos: list, end_pos: list) -> np.array:
    x1, y1 = start_pos[0], start_pos[1]
    x2, y2 = end_pos[0], end_pos[1]
    return image[y1:y2, x1:x2]
