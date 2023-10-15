"""
"""

# TODO: The files in the ./examples/ directory currently doesn't run due to
# python's importing modules issue. We need to specify a better path so we
# can run examples and test it. Fix priorty is high
import cv2
from src.core.imagetranslation import translate

image_path = "images/japanese9.png"
image = cv2.imread(image_path)

translated_image = translate(image, show_borders=True, save_image=True)

cv2.imshow("Original image ", image)
cv2.imshow("Translated Image ", translated_image)
cv2.waitKey()
cv2.destroyAllWindows()
