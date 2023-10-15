"""
This module, imagetranslation, contains the main function that will translate
the image to the destination language. 

TODO Currently, the only supported destination lang is English. We want to be
able to support multiple destination languages in future

TODO Currently, the only supported images are of the following source languages
    - japanese
    - korean
    - mandarin

We want to be able to support multiple languages in future.

"""

import cv2
import numpy as np
import os
import pytesseract

# Modules used
from src.modules.coreimage import calc_max_gap_dist, replace_image_section
from src.modules.fontdetection import calculate_font_size
from src.modules.textdetection import get_sections
from src.modules.textinsertion import manage_text
from src.modules.textsection import (
    should_merge_sections,
    textsection,
    parenttextsection,
)


# Translation APIs
from src.modules.translators.unofficial_google_trans import (
    translate_to_destination_lang,
)


# Helper utilities used
from src.utilities.helpers.imageHelpers import (
    crop_image,
    convert_cv2_to_pil,
    convert_pil_to_cv2,
    calculate_box_width,
    calculate_box_height,
)
from src.utilities.helpers.stringHelpers import remove_trailing_whitespace


# TODO: This needs to be somewhere outside of this file, perhaps in its own
# file
vertical_langauges = [
    "japanese",
    "mandarin",
]


def is_lang_vertical_lang(lang: str) -> bool:
    return lang in vertical_langauges


# TODO: Support for  multiple other source languages and destination languages
# When this is added, make sure to remove default value from src_lang but no
# need to remove default value from dest_lang
# TODO: Need to support robust error handling incase of some failures. As of
# this commit, there virtually exists no error handling...
def translate(
    image: np.array,
    src_lang: str = "japanese",
    dest_lang: str = "english",
    translation_service: str = "python-googletrans",
    show_borders: bool = False,
    save_image: bool = False,
) -> np.array:
    """
    The image to translate its content from source lang to destination lang

    Parameters
    ----------
    image : np.array
        The image to translate its content

    src_lang : str, optional
        The image's primary language to translate from. Default is Japanese

    dest_lang : str, optional
        The language to translate all image's content to. Default is English

    translation_service : str, optional
        The translation API to use. Default is python.googletrans which is free

    show_borders : bool, optional
        Draws borders around detected text regions if True. Default is False

    save_image : bool, optional
        Saves the translated images to the ./results folder. If the folder does
        not exists, it will create one at the root folder. Default is False

    Returns
    -------
    np.array
        The translated image
    """

    # General config sections
    # TODO: Validate the source language before we do any processing

    # TODO: Validate the destination language before we do any processing

    # TODO: Validate if the provided translation service is supported

    # TODO: Validate if proper API credentials are provided in .configs file

    # Start Processing Section
    pytesseract_config = r"--oem 3 --psm 5 -l jpn_vert"

    # TODO: if language is part of vertical text, we MUST rotate it:
    should_rotate = False
    if is_lang_vertical_lang(src_lang):
        should_rotate = True
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    easyocr_sections = get_sections(image, source_lang=src_lang)

    text_sections = []
    for x_min, x_max, y_min, y_max in easyocr_sections:
        text_sections.append(textsection("", [x_min, x_max, y_min, y_max], 12))

    MAXIMUM_GAP_DIST = calc_max_gap_dist(image)
    merged_sections = []

    for section in text_sections:
        if len(merged_sections) == 0:
            merged_sections.append(parenttextsection(section))
            continue

        is_section_merged = False
        for msection in merged_sections:
            if should_merge_sections(
                msection, section, MAXIMUM_GAP_DIST, image
            ):
                is_section_merged = True
                msection.add_section(section)
                break
        if not is_section_merged:
            merged_sections.append(parenttextsection(section))

    destination_image = image.copy()
    for section in merged_sections:
        cropped_section = crop_image(
            destination_image, section.start_pos, section.end_pos
        )

        # TODO: Change the way we mask the original text to remove it from
        # the image. Right now, once we have the merged section, we simply
        # cover it entirely by white and add a black background on the outside
        # so that when we pass it to cv2.inpaint, it "attempts" to inpaint it
        # However, based of examples, this doesnt look as good and thus needs
        # to be revamped....
        border_size = 1
        mask = np.full(
            (
                section.height - border_size * 2,
                section.width - border_size * 2,
                1,
            ),
            255,
            np.uint8,
        )  # white img
        mask = cv2.copyMakeBorder(
            mask,
            top=border_size,
            bottom=border_size,
            left=border_size,
            right=border_size,
            borderType=cv2.BORDER_CONSTANT,
            value=(0, 0, 0),
        )
        processed_cropped_section = cv2.inpaint(
            cropped_section, mask, 7, cv2.INPAINT_NS
        )

        replace_image_section(
            destination_image, processed_cropped_section, section.start_pos
        )

    # TODO: if language is part of vertical text, we MUST rotate it:
    orig_img_height, orig_img_width, _ = destination_image.shape

    if should_rotate:
        destination_image = cv2.rotate(
            destination_image, cv2.ROTATE_90_COUNTERCLOCKWISE
        )
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)

    destination_image_pil = convert_cv2_to_pil(destination_image)
    for section in merged_sections:
        start_pos = []
        end_pos = []
        # TODO: if language is part of vertical text, we MUST rotate it
        if should_rotate:
            start_pos = [
                section.start_pos[1],
                orig_img_width - section.end_pos[0],
            ]
            end_pos = [
                section.end_pos[1],
                orig_img_width - section.start_pos[0],
            ]

        cropped_section = crop_image(image, start_pos, end_pos)
        current_text = ""

        # TODO: if language is part of vertical text, we must use diff config
        if is_lang_vertical_lang(src_lang):
            current_text = pytesseract.image_to_string(
                cropped_section, config=pytesseract_config
            )

        current_text = remove_trailing_whitespace(current_text).replace(
            " ", ""
        )

        if current_text == "":
            continue

        scale = round(orig_img_height / 1000)
        if scale == 0:
            scale = 1

        text_font_size = calculate_font_size(
            current_text, start_pos, end_pos, scale=scale
        )

        translated_text = ""
        if translation_service == "python-googletrans":
            translated_text = translate_to_destination_lang(
                current_text, src_lang
            )
        box = [
            start_pos,
            [end_pos[0], start_pos[1]],
            end_pos,
            [start_pos[0], end_pos[1]],
        ]
        box_width = calculate_box_width(box)
        box_height = calculate_box_height(box)

        destination_image_pil = manage_text(
            destination_image_pil,
            translated_text,
            start_pos,
            box_width,
            box_height,
            text_font_size,
        )

    destination_image = convert_pil_to_cv2(destination_image_pil)

    if show_borders:
        destination_image = cv2.rotate(
            destination_image, cv2.ROTATE_90_CLOCKWISE
        )

        for msection in merged_sections:
            msection.draw_section(destination_image)

        destination_image = cv2.rotate(
            destination_image, cv2.ROTATE_90_COUNTERCLOCKWISE
        )

    # TODO: Add support for saving images to custom path location
    # TODO: Add support for saving images as different file format and
    # different name
    if save_image:
        directory = "results/"
        if not os.path.exists(directory):
            os.makedirs(directory)
        name = "translated_image.png"

        cv2.imwrite(os.path.join(directory, name), destination_image)

    return destination_image
