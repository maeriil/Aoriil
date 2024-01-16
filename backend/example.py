"""
"""

import cv2
import src.core.imagetranslation as imagetranslation

image_path = "images/japanese9.png"
image = cv2.imread(image_path)

translated_image = imagetranslation.translate(
    image, show_borders=True, save_image=True
)

cv2.imshow("Original image ", image)
cv2.imshow("Translated Image ", translated_image)
cv2.waitKey()
cv2.destroyAllWindows()
