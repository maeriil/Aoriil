import modules.textdetection as textdetection
import modules.translateimage as translateimage
import modules.coreimage as coreimage
import utilities.helpers.stringHelpers as strutil
import cv2

# mock Imports
import pytesseract
import os
import math
import numpy as np
from contextlib import redirect_stdout

# reader = easyocr.Reader(['ja', 'en'], gpu = True)
MOCKIMAGEPATH = "images/japanese4.png"
MOCKIMAGESAVEPATH = "results/"
MOCKSECTIONDATAOUTPUTPATH = "results/data.txt"
mock_image = cv2.imread(MOCKIMAGEPATH)
mock_lang = "japanese"
pytesseract_config = r"--oem 3 --psm 5 -l jpn_vert"
_section_val = 0


# Setup Mock Images and functions here
def __display_image(image):
    cv2.imshow("current image is ", image)
    cv2.waitKey()


def __resize_image(image, ratio=0.5):
    cv2.resize(image, (0, 0), fx=ratio, fy=ratio)
    return image


def __write_to_file(image, name):
    cv2.imwrite(os.path.join(MOCKIMAGESAVEPATH, name), image)


# config section
source_lang = mock_lang
image = mock_image.copy()
updated_border_img = image.copy()

# Processing section
text_sections = textdetection.get_text_sections(image, source_lang)
destination_image = image.copy()
mock_image = textdetection._draw_text_borders(mock_image, text_sections)

with open(MOCKSECTIONDATAOUTPUTPATH, "w", encoding="utf-8") as file:
    for box, text, confidence in text_sections:
        (tl, tr, br, bl) = box
        box_format = f"[[{','.join(str(v) for v in tl)}], [{','.join(str(v) for v in tr)}], [{','.join(str(v) for v in br)}], [{','.join(str(v) for v in bl)}]]"
        file.write(box_format + f" {text}" + f" {str(confidence)}\n")

# manual methods
__write_to_file(mock_image, "border.png")

with open("out.txt", "w") as f:
    with redirect_stdout(f):
        new_text_sections = textdetection._merge_overlapping_text_borders(
            text_sections
        )
        updated_border_img = textdetection._draw_text_borders(
            updated_border_img, new_text_sections
        )

with open("results/data2.txt", "w", encoding="utf-8") as file:
    for box, text, confidence in new_text_sections:
        (tl, tr, br, bl) = box
        box_format = f"[[{','.join(str(v) for v in tl)}], [{','.join(str(v) for v in tr)}], [{','.join(str(v) for v in br)}], [{','.join(str(v) for v in bl)}]]"
        file.write(box_format + f" {text}" + f" {str(confidence)}\n")

__write_to_file(updated_border_img, "border-fix.png")
__display_image(mock_image)

for section in new_text_sections:
    _section_val += 1
    print(f"=================SECTION{_section_val}=================")
    (box, current_text, confidence) = section
    cropped_section = coreimage.crop_image(image, box)
    _mock_cropped_section = cropped_section.copy()
    # mask = np.zeros(_mock_cropped_section.shape[:2], dtype="uint8")
    # (x0, y0) = box[0]
    # (x1, y1) = box[2]
    # (x2, y2) = box[1]
    # (x3, y3) = box[3]

    # x_mid0, y_mid0 = midpoint(x1, y1, x2, y2)
    # x_mid1, y_mi1 = midpoint(x0, y0, x3, y3)
    # thickness = int(math.sqrt( (x2 - x1)**2 + (y2 - y1)**2 ))
    # cv2.line(mask, (x_mid0, y_mid0), (x_mid1, y_mi1), 255, thickness)
    (top_left, top_right, bottom_right, bottom_left) = box
    (img_width, img_height) = (
        int(top_right[0] - top_left[0]),
        int(bottom_right[1] - top_right[1]),
    )
    # __display_image(_mock_cropped_section)
    # print('cropped size ', _mock_cropped_section.shape)

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
    # print('mask  size ', mask.shape)
    # mask = coreimage.sharpen_image(_mock_cropped_section)
    # __display_image(mask)
    # __display_image(mask)

    _mock_cropped_section = cv2.inpaint(
        _mock_cropped_section, mask, 3, cv2.INPAINT_TELEA
    )

    # __display_image(_mock_cropped_section)
    # __display_image(image)
    # lower = (0, 0, 0)
    # upper = (255, 255, 255)
    # thresh = cv2.inRange(_mock_cropped_section, lower, upper)
    # mask1 = coreimage.morph_close(thresh, 5)

    # img2 = _mock_cropped_section.copy()
    # img2[mask1 == 0] = (0, 0, 0)
    # _mock_cropped_section = coreimage.sharpen_image(_mock_cropped_section)
    # _mock_image = coreimage.replace_image_section(_mock_image, _mock_cropped_section, box)
    # __display_image(_mock_image)

    # restored_img = cv2.inpaint(
    #     cropped_section, _mock_cropped_section, 11, cv2.INPAINT_TELEA
    # )
    # __display_image(restored_img)

    # translated_text = translateimage._translate_image_to_string(
    # cropped_section, 'japanese'
    # )
    # __display_image(_mock_cropped_section)
    # Add error handling here if required
    current_text = pytesseract.image_to_string(
        cropped_section, config=pytesseract_config
    )
    current_text = strutil.remove_trailing_whitespace(current_text).replace(
        " ", ""
    )
    print(current_text)
    # print('current text ', current_text)

    translated_text = translateimage.translate_to_destination_lang(
        current_text, source_lang
    )
    print(translated_text)
    # translated_text = current_text
    # print('translate', translated_text)
    # print(f"message translated from {current_text} to {translated_text}")
    coreimage.replace_image_section(
        destination_image, _mock_cropped_section, box
    )

    # convert destination image to

    # translated_image = coreimage.draw_text(box, translated_text, _mock_cropped_section)
    destination_image = coreimage.insert_text(
        translated_text, destination_image, box
    ).copy()
    # __display_image(destination_image)
    # cv2.imshow('mock ', _mock_cropped_section) # REMOVE AFTER
    # __display_image(translated_image) # REMOVE AFTER
    # cv2.waitKey()

    # coreimage.replace_image_section(destination_image, translated_image, box)

# display section
cv2.imshow("Untranslated image ", image)
cv2.imshow("Translated image ", destination_image)

# sharpenedDest = coreimage.temp_test(destination_image)
# sharpenedDest = 255 - sharpenedDest
# cv2.imshow("Sharpened image ", sharpenedDest)
cv2.imwrite(
    os.path.join(MOCKIMAGESAVEPATH, "translated.png"), destination_image
)
cv2.waitKey()
cv2.destroyAllWindows()
