#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import numpy as np
import cv2


image = cv2.imread('./test_images/barcode_7.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gaussianBlur = cv2.GaussianBlur(gray, (3, 3), 0)
gradX = cv2.Sobel(gaussianBlur, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
gradY = cv2.Sobel(gaussianBlur, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)
sobelX = cv2.convertScaleAbs(gradX)
sobelY = cv2.convertScaleAbs(gradY)
grad = cv2.subtract(sobelX, sobelY)
sobel = cv2.convertScaleAbs(grad)

blurred = cv2.blur(sobel, (3, 3))
_, barcodeThresh = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY)

barcodeKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 10))
closed = cv2.morphologyEx(barcodeThresh, cv2.MORPH_CLOSE, barcodeKernel)
closed = cv2.erode(closed, None, iterations=4)
closed = cv2.dilate(closed, None, iterations=4)

barcodeContours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
barcodeCnt1 = sorted(barcodeContours, key=cv2.contourArea, reverse=True)[0]
barcodeCnt2 = sorted(barcodeContours, key=cv2.contourArea, reverse=True)[1]
center1, size1, angle1 = cv2.minAreaRect(barcodeCnt1)
center2, size2, angle2 = cv2.minAreaRect(barcodeCnt2)
print(angle1,angle2)
rotated = cv2.getRotationMatrix2D(center2, angle2, 1)
rows, cols, _ = image.shape
rotatedImage = cv2.warpAffine(image, rotated, (cols, rows))

if abs(angle1) > 45:
    rect1 = (center1, size1, 90)
    box1 = np.int0(cv2.boxPoints(rect1))
    temp = [[0, 0]]*4
    for i in range(0, 3):
        temp[i+1] = box1[i]
    temp[0] = box1[3]
    box1 = np.array(temp)
    cv2.drawContours(rotatedImage, [box1], -1, (255, 0, 0), 2)
else:
    rect1 = (center1, size1, 0)
    box1 = np.int0(cv2.boxPoints(rect1))
    cv2.drawContours(rotatedImage, [box1], -1, (255, 0, 0), 2)

if abs(angle2) > 45:
    rect2 = (center2, size2, 90)
    box2 = np.int0(cv2.boxPoints(rect2))
    temp = [[0, 0]]*4
    for i in range(0, 3):
        temp[i+1] = box2[i]
    temp[0] = box2[3]
    box2 = np.array(temp)
    cv2.drawContours(rotatedImage, [box2], -1, (255, 0, 0), 2)
else:
    rect2 = (center2, size2, 0)
    box2 = np.int0(cv2.boxPoints(rect2))
    cv2.drawContours(rotatedImage, [box2], -1, (255, 0, 0), 2)

cv2.imshow('img', rotatedImage)
cv2.waitKey(0)
cv2.destroyAllWindows()


ROI1 = rotatedImage[box1[1][1]+5:box1[0][1]-5, box1[1][0]:box1[2][0]]
ROI2 = rotatedImage[box2[1][1]+5:box2[0][1]-5, box2[1][0]:box2[2][0]]


def detect(ROI):
    defectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 30))
    eroded = cv2.erode(ROI, defectKernel)
    defect = cv2.subtract(ROI, eroded)
    _, defectThresh = cv2.threshold(defect, 25, 255, cv2.THRESH_BINARY)

    b, g, r = cv2.split(defectThresh)
    merged = cv2.merge([r-r, r-r, r])
    defectGray = cv2.cvtColor(merged, cv2.COLOR_BGR2GRAY)
    _, defectGray = cv2.threshold(defectGray, 50, 255, cv2.THRESH_BINARY)
    defectContours, _ = cv2.findContours(defectGray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for ci in defectContours:
        if cv2.contourArea(ci) < 10:
            continue
        x, y, w, h = cv2.boundingRect(ci)
        cv2.rectangle(ROI, (x, y), (x+w, y+h), (0, 0, 255), 2)


detect(ROI1)
detect(ROI2)
cv2.imshow("ROIDetected Image", rotatedImage)
# cv2.imwrite('./result_images/7.png', rotatedImage)

cv2.waitKey(0)
cv2.destroyAllWindows()

