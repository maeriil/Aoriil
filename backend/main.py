import utilities.helpers.stringHelpers as strutil
import utilities.helpers.imageHelpers as imgutil

import modules.textdetection as textdetection
import modules.translators.unofficial_google_trans as translateimage
import modules.coreimage as coreimage
import modules.textsection as textsection
import modules.fontdetection as fontdetection
import modules.textinsertion as textinsertion

import cv2
import numpy as np

# mock imports
import pytesseract
import os

"""
    MOCK Configuration Section
"""
MOCKIMAGEPATH = "images/japanese8.png"
MOCKIMAGESAVEPATH = "results/"
MOCKSECTIONDATAOUTPUTPATH = "results/data.txt"
mock_image = cv2.imread(MOCKIMAGEPATH)
mock_lang = "japanese"
pytesseract_config = r"--oem 3 --psm 5 -l jpn_vert"


def __display_image(image):
    cv2.imshow("current image is ", image)
    cv2.waitKey()


def __resize_image(image, ratio=0.5):
    cv2.resize(image, (0, 0), fx=ratio, fy=ratio)
    return image


def __write_to_file(image, name):
    cv2.imwrite(os.path.join(MOCKIMAGESAVEPATH, name), image)


def __write_array_to_file(name, lst):
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
image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
easyocr_sections = textdetection.get_sections(image, source_lang)
# easyocr_textsections = textdetection.get_text_sections(image, source_lang)
# easyocr_sections = []

# for (box, text) in easyocr_textsections:
#     print(box, text)
#     tl, tr, br, bl = imgutil.unpack_box(box)
#     easyocr_sections.append([tl[0], br[0], tl[1], br[1]])


easyocr_img = image.copy()
result_img = textdetection.draw_text_section_borders(
    easyocr_img, easyocr_sections
)
text_sections = []

for x_min, x_max, y_min, y_max in easyocr_sections:
    curr_section = textsection.textsection(
        "", [x_min, x_max, y_min, y_max], 12
    )
    text_sections.append(curr_section)

merged_sections = []
MAXIMUM_GAP_DIST = coreimage.calc_max_gap_dist(image)
print("MAX Gap distance is: ", MAXIMUM_GAP_DIST)

for section in text_sections:
    if len(merged_sections) == 0:
        curr_section = textsection.parenttextsection(section)
        merged_sections.append(curr_section)
        continue

    is_section_merged = False
    for msection in merged_sections:
        if textsection.should_merge_sections(
            msection, section, MAXIMUM_GAP_DIST, image
        ):
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
__write_to_file(borders_img, "borderim1.png")

destination_image = image.copy()

# process the image now
for section in merged_sections:
    cropped_section = imgutil.crop_image(
        destination_image, section.start_pos, section.end_pos
    )
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
        cropped_section, mask, 7, cv2.INPAINT_NS
    )

    coreimage.replace_image_section(
        destination_image, processed_cropped_section, section.start_pos
    )

rotate_img_height, rotate_img_width, _ = destination_image.shape
destination_image = cv2.rotate(
    destination_image, cv2.ROTATE_90_COUNTERCLOCKWISE
)
image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
destination_image_pil = imgutil.convert_cv2_to_pil(destination_image)

for section in merged_sections:
    print("[============================START===============================]")
    start_pos = [section.start_pos[1], rotate_img_width - section.end_pos[0]]
    end_pos = [section.end_pos[1], rotate_img_width - section.start_pos[0]]

    cropped_section = imgutil.crop_image(image, start_pos, end_pos)
    current_text = pytesseract.image_to_string(
        cropped_section, config=pytesseract_config
    )
    current_text = strutil.remove_trailing_whitespace(current_text).replace(
        " ", ""
    )

    if current_text == "":
        continue

    scale = round(rotate_img_height / 1000)
    if scale == 0:
        scale = 1

    print("current text ", current_text)
    text_font_size = fontdetection.calculate_font_size(
        current_text, start_pos, end_pos, scale=scale
    )
    print("calcd font size ", text_font_size)

    translated_text = translateimage.translate_to_destination_lang(
        current_text, source_lang
    )
    print("translated text ", translated_text)

    box = [
        start_pos,
        [end_pos[0], start_pos[1]],
        end_pos,
        [start_pos[0], end_pos[1]],
    ]

    box_width = imgutil.calculate_box_width(box)
    box_height = imgutil.calculate_box_height(box)
    # destination_image_pil = coreimage.insert_text(
    #     translated_text, destination_image_pil, box, font_size=text_font_size
    # )
    destination_image_pil = textinsertion.manage_text(
        destination_image_pil,
        translated_text,
        start_pos,
        box_width,
        box_height,
        text_font_size,
    )
    print("[============================DONE===============================]")

destination_image = imgutil.convert_pil_to_cv2(destination_image_pil)
cv2.imshow("Untranslated image ", image)
cv2.imshow("Translated image ", destination_image)

destination_image = cv2.rotate(destination_image, cv2.ROTATE_90_CLOCKWISE)
for section in merged_sections:
    destination_image = section.draw_section(destination_image)
destination_image = cv2.rotate(
    destination_image, cv2.ROTATE_90_COUNTERCLOCKWISE
)

cv2.imwrite(
    os.path.join(MOCKIMAGESAVEPATH, "translated-mock.png"), destination_image
)
cv2.waitKey()
cv2.destroyAllWindows()
