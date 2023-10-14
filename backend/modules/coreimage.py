"""
This module, coreimage, contains multiple image processing functions which
can be used to process on the images. All the images are assumed to be of
cv2 image format. 

"""

import cv2
import numpy as np
import math


# TODO: The 7.5 is the current number that works best for our use cases, but
# this needs to be removed and replaced by more logical
def calc_max_gap_dist(image: np.array) -> int:
    """Calculate the maximum gap distance

    This is the maximum distance (in pixels) to merge two bounding boxes
    This current 7.5 pixels is the maximum gap distance for image with
    1000 pixels height

    Parameters
    ----------
    image : np.array
        cv2 image to calculate gap distance

    Returns
    -------
    int
        Maximum gap distance in integer rounded down
    """

    height, _, _ = image.shape
    return math.floor((7.5 * height) / 1000)


# TODO: Support being able to pass the kernel size. Currently the size
# is already hardcoded in the code
def sharpen_image(image: np.array) -> np.array:
    """
    Applies gaussian blur to the image in order to sharpen and remove noise

    Parameters
    ----------
    image : np.array
        The cv2 image to process

    Returns
    -------
    np.array
        The processed cv2 image
    """

    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = cv2.GaussianBlur(image, (9, 9), 0)
    image = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)

    return image


# TODO: Implement this function
def binarize_image(image: np.array) -> np.array:
    """
    Convert the image into a black and white image

    Parameters
    ----------
    image : np.array
        The cv2 image to convert to binary

    Returns
    -------
    np.array
        The processed cv2 image
    """
    pass


# TODO: Implement this function
def inlarge_image(image: np.array) -> np.array:
    """
    Inlarge the size of the image. Does NOT support scaling down of image

    Parameters
    ----------
    image  : np.array
        The cv2 image to inlarge

    Returns
    -------
    np.array
        The inlarged cv2 image
    """
    pass


# TODO: Implement this function
def shrink_image(image: np.array) -> np.array:
    """
    Shrink the size of the image. Does NOT support scaling up of image

    Parameters
    ----------
    image  : np.array
        The cv2 image to shrink

    Returns
    -------
    np.array
        The shrinked cv2 image
    """
    pass


# TODO: Use a Point datatype for start_pos and end_pos
def replace_image_section(
    image: np.array, text_image: np.array, start_pos: list
) -> np.array:
    """
    Replace a section of the image with text_image. The coordinates on the
    the start position is provided by start_pos

    The image and text_image must be of same type.
    The start_pos must refer to point in image and in range of image dimension

    Parameters
    ----------
    image : np.array
        The cv2 image which is going to have its section replaced

    text_image : np.array
        The cv2 image which is image to replace with

    start_pos : list
        The starting [x, y] position to replace in image

    Returns
    -------
        The processed cv2 image
    """

    text_image_height = text_image.shape[0]
    text_image_width = text_image.shape[1]

    x_offset = int(start_pos[0])
    y_offset = int(start_pos[1])

    image[
        y_offset : y_offset + text_image_height,
        x_offset : x_offset + text_image_width,
    ] = text_image

    return image
