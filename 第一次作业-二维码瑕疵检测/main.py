# -*- coding: utf-8 -*-
""" 二维码瑕疵检测 """
import numpy as np
import cv2
import os
import glob
# preprocess the image
def preprocess(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gaussianBlur = cv2.GaussianBlur(gray, (3, 3), 0)
    gradX = cv2.Sobel(gaussianBlur, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
    gradY = cv2.Sobel(gaussianBlur, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)
    # CV_32F --> CV_8U
    sobelX = cv2.convertScaleAbs(gradX)
    sobelY = cv2.convertScaleAbs(gradY)

    grad = cv2.subtract(sobelX,sobelY)
    sobel = cv2.convertScaleAbs(grad)
    blurred = cv2.blur(sobel,(3, 3))
    _, blurred = cv2.threshold(blurred, 180, 255, cv2.THRESH_BINARY)
    return blurred

def getBarCode(binary_img,num_RoI=2):
    barcodeThresh = binary_img
    barcodeKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 10))
    # 图像的闭运算
    closed = cv2.morphologyEx(barcodeThresh, cv2.MORPH_CLOSE, barcodeKernel)
    # 图像的开运算，结构元素是3x3的全1矩阵
    closed = cv2.erode(closed, None, iterations=4)
    closed = cv2.dilate(closed, None, iterations=4)
    barcodeContours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    num_RoI = min(num_RoI, len(barcodeContours))
    barcodeContours = sorted(barcodeContours, key=cv2.contourArea, reverse=True)[0:num_RoI]
    barcodeRect=[{} for i in range(num_RoI)]
    for i in range(num_RoI):
        barcodeRect[i]["center"],barcodeRect[i]["size"],barcodeRect[i]["angle"] = cv2.minAreaRect(barcodeContours[i])
        # if barcodeRect[i]["angle"]+90 <= 1:
        #     barcodeRect[i]["angle"]=-barcodeRect[i]["angle"] - 90
        #     barcodeRect[i]["center"] = barcodeRect[i]["center"][1],barcodeRect[i]["center"][0]
        #     barcodeRect[i]["size"] = barcodeRect[i]["size"][1],barcodeRect[i]["size"][0]
        # print(barcodeRect[i]["center"])
    return barcodeRect


def postprocess(barcodeRect, image, binary_image):
    # print(barcodeRect[0]["angle"])
    # print(barcodeRect[1]["angle"])
    rotated = cv2.getRotationMatrix2D(barcodeRect[1]["center"], barcodeRect[1]["angle"], 1)
    rows, cols, _ = image.shape
    rotated_image = cv2.warpAffine(image, rotated, (cols, rows))
    rotated_binary_image = cv2.warpAffine(binary_image, rotated, (cols, rows))
    _, rotated_binary_image = cv2.threshold(rotated_binary_image, 127, 255, cv2.THRESH_BINARY)
    # cv2.imshow("before",image)
    # cv2.imshow("after",rotated_image)
    # cv2.waitKey(0)
    def getBox(barcodeRect):
        if abs(barcodeRect["angle"]) > 45:
            rect = (barcodeRect["center"], barcodeRect["size"], 90)
            box = np.int0(cv2.boxPoints(rect))
            temp = [[0, 0]] * 4
            for i in range(0, 3):
                temp[i+1] = box[i]
            temp[0] = box[3]
            box = np.array(temp)
        else:
            rect = (barcodeRect["center"], barcodeRect["size"], 0)
            box = np.int0(cv2.boxPoints(rect))
        return box

    RoI = []
    origin_RoI = []
    for rect in barcodeRect:
        box = getBox(rect)
        RoI.append(rotated_binary_image[box[1][1]+5:box[0][1]-5, box[1][0]:box[2][0]])
        origin_RoI.append(rotated_image[box[1][1]+5:box[0][1]-5, box[1][0]:box[2][0]])
    # box1, box2 = getBox(barcodeRect1), getBox(barcodeRect2)
    # RoI1 = rotatedImage[box1[1][1]+5:box1[0][1]-5, box1[1][0]:box1[2][0]]
    # RoI2 = rotatedImage[box2[1][1]+5:box2[0][1]-5, box2[1][0]:box2[2][0]]
    # cv2.imshow("RoI1",RoI1)
    # cv2.imshow("RoI2",RoI2)
    # cv2.waitKey(0)
    return RoI, origin_RoI, rotated_image, rotated_binary_image


def detect(RoI):


    defectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 40))
    # cv2.imshow("ROI",ROI)
    eroded = cv2.erode(RoI, defectKernel)
    # cv2.imshow("eroded",eroded)
    defect = cv2.subtract(RoI, eroded)
    # cv2.imshow("defect",defect)
    _, defectThresh = cv2.threshold(defect, 25, 255, cv2.THRESH_BINARY)
    defectGray = cv2.cvtColor(defectThresh, cv2.COLOR_BGR2GRAY)
    _, defectGray = cv2.threshold(defectGray, 50, 255, cv2.THRESH_BINARY)
    defectContours, _ = cv2.findContours(defectGray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for ci in defectContours:
        if cv2.contourArea(ci) < 30:
            continue
        x, y, w, h = cv2.boundingRect(ci)
        cv2.rectangle(RoI, (x, y), (x+w, y+h), (0, 0, 255), 2)

    # cv2.imshow("result",RoI)
    


if __name__ == "__main__":
    
    img_paths = glob.glob("test_images/*.png")
    if not os.path.exists("result_test_images"):
        os.mkdir("result_test_images")
    for img_path in img_paths:
        # print(img_path)
        # print(img_path[:-4]+"_res.png")
        # continue
        # img_path = "test_images/barcode_3.png"
        image = cv2.imread(img_path)
        # Binarization
        binary_image = preprocess(image)

        # cv2.imshow("image",image)
        # cv2.imshow("binary_image",binary_image)
        # cv2.waitKey(0)
        # return

        barcodeRect = getBarCode(binary_image)

        RoI, origin_RoI, rotated_image, rotated_binary_image = postprocess(barcodeRect, image, binary_image)
        
        # print(RoI[0])
        # detect(origin_RoI[0])
        # print(len(RoI))
        for region in origin_RoI:
            detect(region)
        # detect(RoI1)
        # # detect(RoI2)
        # cv2.imshow("rotated_image", rotated_image)
        # cv2.imshow("rotated_binary_image",rotated_binary_image)
        # cv2.imshow("RoI1",RoI[0])
        # cv2.imshow("RoI2",RoI[1])
        cv2.imwrite("result_"+img_path[:-4]+"_res.png", rotated_image)
        # cv2.waitKey(0)
        cv2.destroyAllWindows()
        # break