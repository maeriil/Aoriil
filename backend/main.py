# from flask import Flask

# app = Flask(__name__)

# @app.route("/")
# def hello_world():
#     return "<p>asdasd!</p>"


#: flask to get data from frontend (assume we have data for now) (last thing we build in backend)
#: OCR or Pytesseract for extracting text from image
#: Pillow library to edit on the images
#: googletrans to translate the text from language 1 to English
#: 

import cv2
import pytesseract
from googletrans import Translator
from manga_ocr import MangaOcr
from PIL import Image

MOCKIMAGEPATH = 'japanese.png'
mockImage = cv2.imread(MOCKIMAGEPATH)
pytesseract_config = r'--oem 3 --psm 5 -l jpn_vert'

grayscale = cv2.cvtColor(mockImage, cv2.COLOR_BGR2GRAY) # convert image to grayscale
blur = cv2.GaussianBlur(grayscale, (9, 9), 0)
# threshold = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

# Attempt to remove noise from image
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
# opening = cv2.morphologyEx(threshold, cv2.MORPH_OPEN, kernel, iterations=1)
# invert = 255 - opening
img = cv2.imread(MOCKIMAGEPATH)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
 
# Performing OTSU threshold
ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
 
# Specify structure shape and kernel size.
# Kernel size increases or decreases the area
# of the rectangle to be detected.
# A smaller value like (10, 10) will detect
# each word instead of a sentence.
rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
 
# Applying dilation on the threshold image
dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
cv2.imshow('dilation ', dilation)
 
# Finding contours
contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL,
                                                 cv2.CHAIN_APPROX_NONE)
 
# Creating a copy of image
im2 = img.copy()
 
# A text file is created and flushed
 
# Looping through the identified contours
# Then rectangular part is cropped and passed on
# to pytesseract for extracting text from it
# Extracted text is then written into the text file
for cnt in contours:
    x, y, w, h = cv2.boundingRect(cnt)
     
    # Drawing a rectangle on copied image
    rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.imshow('rectangle is ', rect)
     
    # Cropping the text block for giving input to OCR
    cropped = im2[y:y + h, x:x + w]
     
    # Open the file in append mode
    file = open("recognized.txt", "a")
     
    # Apply OCR on the cropped image
    text = pytesseract.image_to_string(cropped)
    print(text)

cv2.waitKey()
# jp_text = pytesseract.image_to_string(invert, config=pytesseract_config)
# print(jp_text)

# cv2.imshow('mockimage', mockImage)
# cv2.imshow('blur', blur)
# cv2.imshow('threshold', threshold)
# cv2.imshow('opening', opening)
# cv2.imshow('invert', invert)
# cv2.waitKey()

# translator = Translator()
# translatedText = translator.translate(jp_text, dest="en", src="ja")

# print('[translated]: ', translatedText.text)