import modules.textdetection as textdetection
import modules.translateimage as translateimage
import modules.coreimage as coreimage

import cv2

# mock Imports
import pytesseract
import os
import numpy as np
from contextlib import redirect_stdout

# reader = easyocr.Reader(['ja', 'en'], gpu = True)
MOCKIMAGEPATH = "images/japanese6.png"
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
image = mock_image
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
        # new_text_sections = textdetection._merge_overlapping_text_borders(new_text_sections)
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


exit()

for section in text_sections:
    _section_val += 1
    print(f"=================SECTION{_section_val}=================")
    (box, current_text, confidence) = section
    cropped_section = coreimage.crop_image(image, box)
    _mock_cropped_section = cropped_section.copy()

    # translated_text = translateimage._translate_image_to_string(
    # cropped_section, 'japanese'
    # )

    # Add error handling here if required
    current_text = pytesseract.image_to_string(
        cropped_section, config=pytesseract_config
    )
    # print('current text ', current_text)

    translated_text = translateimage.translate_to_destination_lang(
        current_text, source_lang
    )
    # print('translate', translated_text)
    print(f"message translated from {current_text} to {translated_text}")

    translated_image = coreimage.draw_text(box, translated_text)
    # cv2.imshow('mock ', _mock_cropped_section) # REMOVE AFTER
    # __display_image(translated_image) # REMOVE AFTER
    # cv2.waitKey()

    coreimage.replace_image_section(destination_image, translated_image, box)

# display section
cv2.imshow("Untranslated image ", image)
cv2.imshow("Translated image ", destination_image)
cv2.imwrite(
    os.path.join(MOCKIMAGESAVEPATH, "translated.png"), destination_image
)
cv2.waitKey()
cv2.destroyAllWindows()
