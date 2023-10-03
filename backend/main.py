# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>asdasd!</p>"

#: flask to get data from frontend (assume we have data for now)
# (last thing we build in backend)
#: OCR or Pytesseract for extracting text from image
#: googletrans to translate the text from language 1 to English
#:

import cv2
# import pytesseract
import easyocr
import numpy as np

# from pytesseract import Output
# from manga_ocr import MangaOcr
from googletrans import Translator
from PIL import Image

import modules.textExtractor as module1

# import modules.coreimage as img
import modules.translateImage as trnsl
import modules.nyorem as ny


MOCKIMAGEPATH = "images/GrandBlue/Grand Blue v01-06/Grand_Blue_v01/Grand Blue v01/GranB01_193.jpg"
mockImage = cv2.imread(MOCKIMAGEPATH)
pytesseract_config = r"--oem 3 --psm 5 -l jpn_vert"

# module1.cropImageToText(mockImage)

# convert image to grayscale
grayscale = cv2.cvtColor(mockImage, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(grayscale, (3, 3), 0)
threshold = cv2.threshold(
    blur, 0, 255,
    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Attempt to remove noise from image
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=1)
invert = 255 - opening
# img = cv2.imread(MOCKIMAGEPATH)
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# # Performing OTSU threshold
# ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

# # Specify structure shape and kernel size.
# # Kernel size increases or decreases the area
# # of the rectangle to be detected.
# # A smaller value like (10, 10) will detect
# # each word instead of a sentence.
# rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

# # Applying dilation on the threshold image
# dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)
# cv2.imshow("dilation ", dilation)

# # Finding contours
# contours, hierarchy = cv2.findContours(
#     dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
# )

# # Creating a copy of image
# im2 = img.copy()

# # A text file is created and flushed

# # Looping through the identified contours
# # Then rectangular part is cropped and passed on
# # to pytesseract for extracting text from it
# # Extracted text is then written into the text file
# for cnt in contours:
#     x, y, w, h = cv2.boundingRect(cnt)

#     # Drawing a rectangle on copied image
#     rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
#     cv2.imshow("rectangle is ", rect)

#     # Cropping the text block for giving input to OCR
#     cropped = im2[y: y + h, x: x + w]

#     # Open the file in append mode
#     file = open("recognized.txt", "a")

#     # Apply OCR on the cropped image
#     text = pytesseract.image_to_string(cropped)
#     print(text)

# cv2.waitKey()
# sampleImg = pytesseract.image_to_boxes(invert, config=pytesseract_config)
# print('start')
# print(sampleImg)
# print('done')

# jp_text = pytesseract.image_to_string(invert, config=pytesseract_config)
# print(jp_text)

# # cv2.imshow("mockimage", mockImage)
# # cv2.imshow("blur", blur)
# # cv2.imshow("threshold", threshold)
# # cv2.imshow("opening", opening)
# # cv2.imshow("invert", invert)
# # cv2.waitKey()

# small = cv2.resize(mockImage, (0,0), fx=0.25, fy=0.25)
# small = mockImage.copy()
# mockCoreImage = img.CoreImage(small)
# test = mockCoreImage.sharpenImage()
# contours, hierarchy = mockCoreImage.getTextSections(test)


# textContent = pytesseract.image_to_string(small, config=pytesseract_config)
# print('text content is ', textContent)

# print(f"Naive way is returning {len(contours)} contours")
# cv2.drawContours(small, contours, -1, (0, 255, 0), 2)
# cv2.imshow('naive ', small)
# cv2.waitKey()
# print('now using mocr')

# convertedColours = cv2.cvtColor(mockImage, cv2.COLOR_BGR2RGB)
# convertedPIL = Image.fromarray(convertedColours)

# textContent = mocr(convertedPIL)
# print(textContent)

# cv2.imshow("mock Image ", mockImage)
# cv2.waitKey()

# for contour in contours:
#     print('init cropImage method')

#     x, y, width, height = cv2.boundingRect(contour)
#     croppedImage = test[y:y+height, x:x+width]

#     # textContent = trnsl.translateImageToString(croppedImage, "japanese")
#     textContent = pytesseract.image_to_string(croppedImage, config=pytesseract_config)
#     print(textContent)

#     cv2.imshow('current cropped image ', croppedImage)
#     cv2.waitKey()

# translatedTextContent = trnsl.translateJapaneseStringToDestString(textContent.Text)

# print(translatedTextContent)

# print('py-box', pytesseract.image_to_boxes(mockImage))
# print('py-data', pytesseract.image_to_data(mockImage))
# print('py-osd', pytesseract.image_to_osd(mockImage))

# d = pytesseract.image_to_data(mockImage, output_type=Output.DICT)
# n_boxes = len(d['level'])
# for i in range(n_boxes):
#     convidence = d['conf'][i]
#     if convidence == -1:
#         print(convidence)
#         (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
#         cv2.rectangle(mockImage, (x, y), (x + w, y + h), (0, 255, 0), 2)

# cv2.imshow('mock image ', mockImage)
# cv2.waitKey()

reader = easyocr.Reader(['ja', 'en'], gpu=True)
# mockImage = invert.copy()
img = cv2.imread(MOCKIMAGEPATH)
orig = img.copy()
# mockImage = cv2.resize(img, (0,0), fx=2.5, fy=2.5)
# img = mockImage

tempImg = img.copy()
tempImg = cv2.cvtColor(tempImg, cv2.COLOR_BGR2GRAY)

        # Add blur to the image
        # TODO extract the gaussian kernal to global scope and make it a constant
        # TODO Consider using median blur instead to reduce noise
tempImg = cv2.GaussianBlur(tempImg, (5, 5), 0)    

        # Using otsu threshold to convert image to binary image
tempImg = cv2.threshold(
            tempImg, 0, 255,
            cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
        
        # Attempt to remove noise from the image
        # extract the kernal matrix to global scope and make it a constant
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        # Apply Errosion then dialation using morphologyEx
tempImg = cv2.morphologyEx(tempImg, cv2.MORPH_OPEN, kernel, iterations=1)

        # Invert the image colours
tempImg = 255 - tempImg
cv2.imshow('temp img ', tempImg)
cv2.waitKey()

# img = tempImg

results = reader.readtext(img)
boxes = []

for (box, text, conf) in results:
    (tl, tr, br, bl) = box
    tl = (int(tl[0]), int(tl[1]))
    tr = (int(tr[0]), int(tr[1]))
    br = (int(br[0]), int(br[1]))
    bl = (int(bl[0]), int(bl[1]))

    cv2.rectangle(img, tl, br, (0, 255, 0), 2)
    x = int(tl[0])
    y = int(tl[1])
    x1 = int(br[0])
    y1 = int(br[1])
    boxes.append([[x, y], [x1, y1]])
print('current boxes size is ', len(boxes))
cv2.imshow('mock image test ', img)
cv2.waitKey()



# tuplify
def tup(point):
    return (point[0], point[1])


# returns true if the two boxes overlap
def overlap(source, target):
    # unpack points
    tl1, br1 = source
    tl2, br2 = target

    # checks
    if tl1[0] >= br2[0] or tl2[0] >= br1[0]:
        return False
    if tl1[1] >= br2[1] or tl2[1] >= br1[1]:
        return False
    return True


# returns all overlapping boxes
def getAllOverlaps(boxes, bounds, index):
    overlaps = []
    for a in range(len(boxes)):
        if a != index:
            if overlap(bounds, boxes[a]):
                overlaps.append(a)
    return overlaps


def medianCanny(img, thresh1, thresh2):
    median = np.median(img)
    img = cv2.Canny(img, int(thresh1 * median), int(thresh2 * median))
    return img


# each element is [[top-left], [bottom-right]];
# hierarchy = hierarchy[0]
# for component in zip(contours, hierarchy):
#     currentContour = component[0]
#     currentHierarchy = component[1]
#     x, y, w, h = cv2.boundingRect(currentContour)
#     if currentHierarchy[3] < 0:
#         cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 1)
#         boxes.append([[x, y], [x + w, y + h]])

# filter out excessively large boxes
filtered = []
max_area = 30000
for box in boxes:
    w = box[1][0] - box[0][0]
    h = box[1][1] - box[0][1]
    if w * h < max_area:
        filtered.append(box)
boxes = filtered

# go through the boxes and start merging
merge_margin = 15

# this is gonna take a long time
finished = False
highlight = [[0, 0], [1, 1]]
points = [[[0, 0]]]
while not finished:
    # set end con
    finished = True

    # check progress
    print("Len Boxes: " + str(len(boxes)))

    # draw boxes # comment this section out to run faster
    copy = np.copy(img)
    for box in boxes:
        cv2.rectangle(copy, tup(box[0]), tup(box[1]), (0, 200, 0), 1)
    cv2.rectangle(copy, tup(highlight[0]), tup(highlight[1]), (0, 0, 255), 2)
    for point in points:
        point = point[0]
        cv2.circle(copy, tup(point), 4, (255, 0, 0), -1)
    cv2.imshow("Copy", copy)
    key = cv2.waitKey(1)
    if key == ord("q"):
        break

    # loop through boxes
    index = len(boxes) - 1
    while index >= 0:
        # grab current box
        curr = boxes[index]

        # add margin
        tl = curr[0][:]
        br = curr[1][:]
        tl[0] -= merge_margin
        tl[1] -= merge_margin
        br[0] += merge_margin
        br[1] += merge_margin

        # get matching boxes
        overlaps = getAllOverlaps(boxes, [tl, br], index)

        # check if empty
        if len(overlaps) > 0:
            # combine boxes
            # convert to a contour
            con = []
            overlaps.append(index)
            for ind in overlaps:
                tl, br = boxes[ind]
                con.append([tl])
                con.append([br])
            con = np.array(con)

            # get bounding rect
            x, y, w, h = cv2.boundingRect(con)

            # stop growing
            w -= 1
            h -= 1
            merged = [[x, y], [x + w, y + h]]

            # highlights
            highlight = merged[:]
            points = con

            # remove boxes from list
            overlaps.sort(reverse=True)
            for ind in overlaps:
                del boxes[ind]
            boxes.append(merged)

            # set flag
            finished = False
            break

        # increment
        index -= 1
cv2.destroyAllWindows()
copy = np.copy(orig)
print('there are ', len(boxes))
for box in boxes:
    copy = cv2.rectangle(copy, tup(box[0]), tup(box[1]), (0, 255, 0), 1)
cv2.imshow("Final", copy)
cv2.waitKey(0)

