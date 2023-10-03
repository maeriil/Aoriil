import cv2
import numpy

def cropImageToText (image):
    originalImage = image.copy()

    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(grayscale, (3, 3), 0)
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25,1))
    detected_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
    cnts = cv2.findContours(detected_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]
    for c in cnts:
        cv2.drawContours(thresh, [c], -1, 0, -1)
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,30))
    dilate = cv2.dilate(thresh, vertical_kernel, iterations=3)

    cnts, _ = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:-1]

    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)
        cv2.rectangle(image, (x, y), (x + w, y + h), (36,255,12), 4)
        ROI = originalImage[y:y+h, x:x+w]
        break

    cv2.imshow('image', image)
    cv2.imshow('dilate', dilate)
    cv2.imshow('thresh', thresh)
    cv2.imshow('ROI', ROI)
    cv2.waitKey()
    



def textExtractor (image):
    return image