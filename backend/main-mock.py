import utilities.helpers.stringHelpers as strutil
import utilities.helpers.imageHelpers as imgutil

import modules.textdetection as textdetection
import modules.translateimage as translateimage
import modules.coreimage as coreimage
import modules.textsection  as  textsection
import modules.fontdetection as fontdetection

import cv2
import math
import numpy as np

# mock imports
import pytesseract
import os

"""
    MOCK Configuration Section
"""
MOCKIMAGEPATH = "images/japanese5.png"
MOCKIMAGESAVEPATH = "results/"
MOCKSECTIONDATAOUTPUTPATH = "results/data.txt"
mock_image = cv2.imread(MOCKIMAGEPATH)
mock_lang = "japanese"
pytesseract_config = r"--oem 3 --psm 5 -l jpn_vert"
_section_val = 0

def __display_image(image):
    cv2.imshow("current image is ", image)
    cv2.waitKey()


def __resize_image(image, ratio=0.5):
    cv2.resize(image, (0, 0), fx=ratio, fy=ratio)
    return image


def __write_to_file(image, name):
    cv2.imwrite(os.path.join(MOCKIMAGESAVEPATH, name), image)

def __write_array_to_file (name, lst):
    with open(name, "w", encoding="utf-8") as file:
        for vals in lst:
            file.write(vals.__str__())
    file.close()


"""
    General Configuration Section
"""

source_lang = mock_lang
image = mock_image.copy()
updated_border_img = image.copy()


"""
    Start Processing Section
"""
destination_image = image.copy()
easyocr_sections = textdetection.get_sections(image, source_lang)
text_sections = []

for (x_min, x_max, y_min, y_max) in easyocr_sections:
    cropped_section = imgutil.crop_image(image, [x_min, y_min], [x_max, y_max])
    current_text = pytesseract.image_to_string(
        cropped_section, config=pytesseract_config
    )
    current_text = strutil.remove_trailing_whitespace(current_text).replace(
        " ", ""
    )
    print('curr text', current_text)
    font_size = fontdetection.calculate_font_size(current_text, [x_min, y_min], [x_max, y_max])
    curr_section = textsection.textsection(current_text, [x_min, x_max, y_min, y_max], font_size)
    text_sections.append(curr_section)

merged_sections = []
MAXIMUM_GAP_DIST = coreimage.calc_max_gap_dist(image)

for section in text_sections:
    if len(merged_sections) == 0:
        curr_section = textsection.parenttextsection(section)
        merged_sections.append(curr_section)
        continue

    is_section_merged = False
    for msection in merged_sections:
        if textsection.should_merge_sections(msection, section, MAXIMUM_GAP_DIST, image):
            is_section_merged = True
            msection.add_section(section)
            break
    if not is_section_merged:
        curr_section = textsection.parenttextsection(section)
        merged_sections.append(curr_section)

__write_array_to_file(MOCKIMAGESAVEPATH + "fixdata.txt", text_sections)
__write_array_to_file(MOCKIMAGESAVEPATH + "fixdatamerge.txt", merged_sections)

# technically should be merged now:

borders_img = image.copy()
for section in merged_sections:
    borders_img = section.draw_section(borders_img)
__display_image(borders_img)
__write_to_file(borders_img, "borderim1.png")

# process the image now
for section in merged_sections:
    cropped_section = imgutil.crop_image(destination_image, section.start_pos, section.end_pos)
    img_width = section.width
    img_height = section.height

    border_size = 1
    mask = np.full(
        (img_height - border_size * 2, img_width - border_size * 2, 1),
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
        cropped_section, mask, 3, cv2.INPAINT_TELEA
    )

    # TODO: REMOVE BOX and replace with start_pos, end_pos
    box = [section.start_pos, [section.end_pos[0], section.start_pos[1]], section.end_pos, [section.start_pos[0], section.end_pos[1]]]
    coreimage.replace_image_section(destination_image, processed_cropped_section, box)

__display_image(destination_image)
destination_image_pil = imgutil.convert_cv2_to_pil(destination_image)

for section in merged_sections:
    cropped_section = imgutil.crop_image(image, section.start_pos, section.end_pos)
    __display_image(cropped_section)
    current_text = pytesseract.image_to_string(
        cropped_section, config=pytesseract_config
    )
    current_text = strutil.remove_trailing_whitespace(current_text).replace(
        " ", ""
    )
    translated_text = translateimage.translate_to_destination_lang(
        current_text, source_lang
    )

    box = [section.start_pos, [section.end_pos[0], section.start_pos[1]], section.end_pos, [section.start_pos[0], section.end_pos[1]]]
    print('current text ', current_text)
    print('translated text ', translated_text)
    destination_image_pil = coreimage.insert_text(
        translated_text, destination_image_pil, box
    )

destination_image = imgutil.convert_pil_to_cv2(destination_image_pil)
cv2.imshow("Untranslated image ", image)
cv2.imshow("Translated image ", destination_image)
cv2.imwrite(
    os.path.join(MOCKIMAGESAVEPATH, "translated-mock.png"), destination_image
)
cv2.waitKey()
cv2.destroyAllWindows()