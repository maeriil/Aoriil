import modules.textdetection as textdetection
import modules.translateimage as translateimage
import modules.coreimage as coreimage

import cv2

# mock Imports
import pytesseract
import os


# Setup Mock Images and functions here
def __display_image(image):
    cv2.imshow("current image is ", image)
    cv2.waitKey()


def __resize_image(image, ratio=0.5):
    cv2.resize(image, (0, 0), fx=ratio, fy=ratio)
    return image


# reader = easyocr.Reader(['ja', 'en'], gpu = True)
MOCKIMAGEPATH = "images/japanese3.png"
MOCKIMAGESAVEPATH = "results/"
mock_image = cv2.imread(MOCKIMAGEPATH)
mock_lang = "japanese"
pytesseract_config = r"--oem 3 --psm 5 -l jpn_vert"

# config section
source_lang = mock_lang
image = mock_image

# Processing section
text_sections = textdetection.get_text_sections(image, source_lang)
destination_image = image.copy()

for section in text_sections:
    (box, current_text, confidence) = section
    cropped_section = coreimage.crop_image(image, box)

    # __display_image(cropped_section) # REMOVE AFTER
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

    translated_image = coreimage.draw_text(box, translated_text)

    # __display_image(translated_image) # REMOVE AFTER

    coreimage.replace_image_section(destination_image, translated_image, box)

# display section
cv2.imshow("Untranslated image ", image)
cv2.imshow("Translated image ", destination_image)
cv2.imwrite(
    os.path.join(MOCKIMAGESAVEPATH, "translated.png"), destination_image
)
cv2.waitKey()
cv2.destroyAllWindows()
