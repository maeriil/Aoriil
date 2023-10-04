import cv2
import numpy


# TODO: add documentation and explain each step
def sharpenImage(image):
    # Convert the image to grayscale format
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Add blur to the image
    # extract the gaussian kernal to global scope and make it a constant
    image = cv2.GaussianBlur(image, (9, 9), 0)

    # use threshold to do TODO: WHAT?
    image = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )[1]

    # Attempt to remove noise from the image
    # extract the kernal matrix to global scope and make it a constant
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    # What does this do? TODO
    image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)

    # Invert the image colours
    image = 255 - image

    return image
