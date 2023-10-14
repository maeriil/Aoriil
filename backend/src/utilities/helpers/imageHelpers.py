"""
This module, imageHelpers, contains useful functions related to image
processing and other general stuff

If there is a image function used by at least two other functions, consider
placing the function here to follow D.R.Y Principles

"""

import cv2
import numpy as np

from PIL import Image


def convert_cv2_to_pil(image: np.array) -> Image.Image:
    """
    Convert cv2 image to Pillow Image

    Parameters
    ----------
    image : np.array
        The cv2 image to convert

    Returns
    -------
    Image.Image
        The converted Pillow Image
    """

    conv_image_color = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(conv_image_color)
    return image_pil


def convert_pil_to_cv2(image: Image.Image) -> np.array:
    """
    Convert Pillow image to cv2 Image

    Parameters
    ----------
    image : Image.Image
        The Pillow image to convert

    Returns
    -------
    np.array
        The converted cv2 Image
    """

    return np.asarray(image)


def unpack_box(box: list) -> (list, list, list, list):
    """
    Unpacks the bounding box properly

    Parameters
    ----------
    box : list
        The bounding box containing 4 points in the following format:
        [top_left, top_right, bottom_right, bottom_left]

    Returns
    -------
    list
        The top left point of format [x, y]

    list
        The top right point of format [x, y]

    list
        The bottom right point of format [x, y]

    list
        The bottom left point of format [x, y]

    Raises
    ------
    ValueError
        If box is not provided and box does not contain only 4 elements
    """

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
    """
    Calculates the width between the two x coordinates

    Parameters
    ----------
    left_point_x : int
        The x coordinate of the first point

    right_point_x : int
        The x coordinate of the second point

    Returns
    -------
    int
        The width between the two x coordinates
    """

    return abs(left_point_x - right_point_x)


def calculate_box_width(box) -> int:
    """
    Calculates the width of the bounding box

    Parameters
    ----------
    box : list
        The bounding box containing the four points in the following format
        [top_left, top_right, bottom_right, bottom_left]

    Returns
    -------
    int
        The width of the bounding box
    """

    top_left, top_right, _, _ = unpack_box(box)

    return calculate_width(top_left[0], top_right[0])


def calculate_height(left_point_y: int, right_point_y: int) -> int:
    """
    Calculates the height between the two y coordinates

    Parameters
    ----------
    left_point_y : int
        The y coordinate of the first point

    right_point_y : int
        The y coordinate of the second point

    Returns
    -------
    int
        The height between the two y coordinates
    """

    return abs(left_point_y - right_point_y)


def calculate_box_height(box) -> int:
    """
    Calculates the height of the bounding box

    Parameters
    ----------
    box : list
        The bounding box containing the four points in the following format
        [top_left, top_right, bottom_right, bottom_left]

    Returns
    -------
    int
        The height of the bounding box
    """

    top_left, _, _, bottom_left = unpack_box(box)

    return calculate_height(top_left[1], bottom_left[1])


def crop_image(image: np.array, start_pos: list, end_pos: list) -> np.array:
    """
    Crops the cv2 image from start_pos to end_pos in rectangular shape

    Parameters
    ----------
    image : np.array
        The original image to crop a selection from

    start_pos : list
        The starting point of the bounding box. It is of format [x, y]

    end_pos : list
        The ending point of the bounding box. It is of format [x, y]

    Returns
    -------
    np.array
        The cropped cv2 image
    """

    x1, y1 = start_pos[0], start_pos[1]
    x2, y2 = end_pos[0], end_pos[1]
    return image[y1:y2, x1:x2]
