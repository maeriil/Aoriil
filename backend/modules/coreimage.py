import cv2
import numpy as np

class CoreImage:
    def __init__ (self, image):
        self.image = image

    def sharpenImage (self):
        # Convert the image to grayscale format
        tempImg = self.image.copy()
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

        # cv2.imshow("invert image ", tempImg)
        # cv2.waitKey()

        return tempImg

    # def cropImage (self, contour):
    #     print('init cropImage method')

    #     x, y, width, height = cv2.boundingRect(contour)
    #     croppedImage = self.image[y:y+height, x:x+width]

    #     return croppedImage
    

    def getTextSections(self, sharpenedImage):
        print('init getTextSection method')
        # temporaryImage = self.image.copy()
        # temporaryImage = self.sharpenImage()
        # ret, ctrs, _ = cv2.findContours(temporaryImage, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # sections = []
        # for ctr in ctrs:
        #     x, y, w, h = cv2.boundingRect(ctr)
        #     section = self.cropImage(self.image, ctr)
        #     sections.append(section)

        if sharpenedImage is None:
            print("did not pass parameters?")
            return

        contours, hierarchy = cv2.findContours(
            sharpenedImage,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        # for contour in contours:
        #     # print('countour is ', contour)
        #     x, y, width, height = cv2.boundingRect(contour)
        #     cv2.rectangle(sharpenedImage, (x, y), (x + width, y + height), (0, 255, 255), 2)
        
        # cv2.imshow('sharpen image ', sharpenedImage)
        # cv2.waitKey()

        return contours, hierarchy

