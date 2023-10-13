"""
This module, textdetection, contains primarily the easyocr's detection
functions. In future, if we plan on switching over to different OCRs, their
functions should be added in this file instead.

"""

import cv2
import numpy as np
import easyocr

import utilities.helpers.imageHelpers as imgutil


# TODO: Should this be initalized here or on the main file? Find better place
# easy ocr's readers for the following languages
readers = {
    "japanese": easyocr.Reader(["ja"], gpu=False),
    "korean": easyocr.Reader(["ko", "en"], gpu=True),
    "chinese_sim": easyocr.Reader(["ch_sim", "en"], gpu=True),
}


# TODO: Error handling for this function
# TODO: Does this function really belong to this module? Find better place
def draw_text_borders(image: np.array, borders_list: list) -> np.array:
    """
    Draws a rectangular green coloured borders around the image based on
    boxes provided in borders_list

    Parameters
    ----------
    image : np.array
        The cv2 image to draw the borders on

    borders_list : list
        The list of boxes containing points in each bounding boxes

    Returns
    -------
    np.array
        The cv2 image containing the borders of bounding boxes

    """
    border_color = (0, 255, 0)
    border_pixel = 1

    for box, _, _ in borders_list:
        (tl, _, br, _) = imgutil.unpack_box(box)

        cv2.rectangle(
            image, tl, br, color=border_color, thickness=border_pixel
        )

    return image


# TODO: Error handling for this function
# TODO: Does this function really belong to this module? Find better place
def draw_text_section_borders(image: np.array, sections: list) -> np.array:
    """
    Draws a rectangular green coloured borders around the image based on
    [x_1, x_2, y_1, y_2] coordinates provided in sections

    Parameters
    ----------
    image : np.array
        The cv2 image to draw the borders on

    sections : list
        The list of section containing 4 points, [xmin, xmax, ymin, ymax]

    Returns
    -------
    np.array
        The cv2 image containing the borders of bounding boxes

    """
    border_color = (0, 255, 0)
    border_pixel = 1
    for xmin, xmax, ymin, ymax in sections:
        tl = (int(xmin), int(ymin))
        br = (int(xmax), int(ymax))

        cv2.rectangle(
            image, tl, br, color=border_color, thickness=border_pixel
        )
    return image


# TODO: Currently width_ths and height_ths are set values based on what
# we we found best for our purposes. Is this really the best values we
# can provide? Furthermore, when should we be adding values like this
# TODO: Are there other parameters we can provide to easyocr's readtext to
# further increase detection for given languages? Needs to research
def get_sections(image: np.array, source_lang: str = "japanese") -> list:
    """
    Get all the bounding sections based off easyocr's detection

    Parameters
    ----------
    image : np.array
        The cv2 image to detect characters from

    source_lang : str
        The source language of the image. Default is japanese

    Returns
    -------
    list
        The list containing sections for ever character it was able to detect
        The section looks like [xmin, xmax, ymin, ymax]

    """
    horz, _ = readers[source_lang].detect(
        image,
        width_ths=0.55,
        height_ths=0.55,
    )
    return horz[0]


# TODO: Currently width_ths and height_ths are set values based on what
# we we found best for our purposes. Is this really the best values we
# can provide? Furthermore, when should we be adding values like this
# TODO: Should paragraph=True really be used? Does it increase or decrease the
# sentence detection error percent.
# TODO: Are there other parameters we can provide to easyocr's readtext to
# further increase detection for given languages? Needs to research
def get_text_sections(image: np.array, source_lang: str = "japanese") -> list:
    """
    Get the bounding box, text and confidence based off easyocr's detection

    Parameters
    ----------
    image : np.array
        The cv2 image to detect characters from

    source_lang : str
        The source language of the image. Default is japanese

    Returns
    -------
    list
        The list containing boxes, text and confidence of each detected section
        Each point in the box is a Point [x, y] in the image
        [[top_left, top_right, bottom_right, bottom_left], text, confidence]

    """
    return readers[source_lang].readtext(
        image, width_ths=0.55, height_ths=0.55, paragraph=True
    )
