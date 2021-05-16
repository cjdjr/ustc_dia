import cv2
import argparse
import struct
import numpy as np
import math
import copy
from matplotlib import pyplot as plt
def normlize(data):
    np_data=np.array(data)
    return list(np_data / math.sqrt((np_data**2).sum()))

def get_rotate_matrix(theta):
    return np.array([[math.cos(theta),math.sin(theta)],[-math.sin(theta),math.cos(theta)]])

def drawMatches(img1, kp1, img2, kp2, color=(0,0,255),out = None):
   
    rows1 = img1.shape[0]
    cols1 = img1.shape[1]
    rows2 = img2.shape[0]
    cols2 = img2.shape[1]

    if out is None:
        out = np.zeros((max([rows1,rows2]),cols1+cols2,3), dtype='uint8')

        out[:rows1,:cols1] = np.dstack([img1])

        out[:rows2,cols1:] = np.dstack([img2])
    
    for i in range(len(kp1)):
        x1,y1 = kp1[i]
        x2,y2 = kp2[i]
        cv2.line(out, (int(np.round(x1)),int(np.round(y1))), (int(np.round(x2)+cols1),int(np.round(y2))),color, 1, shift=0)  #画线，cv2.line()参考官方文档

    return out


class Feature(object):
    def __init__(self,data):
        super().__init__()
        self.num = struct.unpack('i', data[:4])[0]
        self.sift = []
        self.para = []
        for base in range(4,len(data),128+16):
            self.sift.append(normlize(struct.unpack('128B',data[base:base+128])))
            self.para.append(struct.unpack('4f',data[base+128:base+128+16]))
        self.sift = np.array(self.sift)
        self.para = np.array(self.para)
        # print(len(self.sift))
        # print(len(self.para))
        # print(self.para[0])

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--img_1', type=str,default='./test_images/4.jpg')
    parser.add_argument('--img_2', type=str,default='./test_images/148.jpg')
    parser.add_argument('--threshold', type=float,default=0.2)
    parser.add_argument('--threshold_factor', type=float,default=0.8)
    parser.add_argument('--r', type=int,default=4)
    args = parser.parse_args()
    return args

def main(args):
    sift_file = args.img_1+".sift"
    with open(sift_file, 'rb') as f:
        data = f.read()
    img1_feature = Feature(data)
    img1 = cv2.imread(args.img_1)

    sift_file = args.img_2+".sift"
    with open(sift_file, 'rb') as f:
        data = f.read()
    img2_feature = Feature(data)
    img2 = cv2.imread(args.img_2)
    
    # output = drawMatches(img1,None,img2,None,None)
    # plt.figure()
    # plt.imshow(output)
    # plt.show()
    # plt.subplot(1,2,1)
    # plt.imshow(img1)
    # plt.subplot(1,2,2)
    # plt.imshow(img2)
    # plt.show()

    match = [-1 for i in range(img1_feature.num)]
    for i in range(img1_feature.num):
        d = ((img1_feature.sift[i] - img2_feature.sift)**2).sum(axis=1)
        index = d.argmin()
        if d[index] < args.threshold:
            match[i] = index
    
    map1=[]
    map2=[]
    for i in range(img1_feature.num):
        if match[i]!=-1:
            map1.append(img1_feature.para[i][0:2])
            map2.append(img2_feature.para[match[i]][0:2])
    map1=np.array(map1)
    map2=np.array(map2)

    output = drawMatches(img1,map1,img2,map2)


    match_num = sum(np.array(match)!=-1)

    GX1=[]
    GY1=[]
    GX2=[]
    GY2=[]

    for k in range(args.r):
        theta = (k-1)*math.pi/(2*args.r)
        rotate_matrix = get_rotate_matrix(theta)
        G1 = np.matmul(map1,rotate_matrix)
        G2 = np.matmul(map2,rotate_matrix)

        _GX1 = np.expand_dims(G1[:,0], axis=1).repeat(match_num,axis=1) >= G1[:,0]
        _GY1 = np.expand_dims(G1[:,1], axis=1).repeat(match_num,axis=1) >= G1[:,1]
        _GX2 = np.expand_dims(G2[:,0], axis=1).repeat(match_num,axis=1) >= G2[:,0]
        _GY2 = np.expand_dims(G2[:,1], axis=1).repeat(match_num,axis=1) >= G2[:,1]

        GX1.append(_GX1)
        GX2.append(_GX2)
        GY1.append(_GY1)
        GY2.append(_GY2)

    GX1=np.array(GX1).transpose((1,2,0))
    GX2=np.array(GX2).transpose((1,2,0))
    GY1=np.array(GY1).transpose((1,2,0))
    GY2=np.array(GY2).transpose((1,2,0))
        
    Vx = np.logical_xor(GX1,GX2)
    Vy = np.logical_xor(GY1,GY2)

    del_kp1 = []
    del_kp2 = []

    threshold = math.floor(args.threshold_factor*match_num)
    for i in range(match_num):
        Sx = Vx.sum(axis=2).sum(axis=1)
        index=Sx.argmax()
        if Sx[index] > threshold:
            del_kp1.append(map1[index])
            del_kp2.append(map2[index])
            Vx[index,:,:] = 0
            Vx[:,index,:] = 0
            Vy[index,:,:] = 0
            Vy[:,index,:] = 0

        Sy = Vy.sum(axis=2).sum(axis=1)
        index=Sy.argmax()
        if Sy[index] > threshold:
            del_kp1.append(map1[index])
            del_kp2.append(map2[index])
            Vx[index,:,:] = 0
            Vx[:,index,:] = 0
            Vy[index,:,:] = 0
            Vy[:,index,:] = 0

    output = drawMatches(img1,del_kp1,img2,del_kp2,(255,0,0),output)

    plt.figure()
    plt.imshow(output)
    plt.show()


if  __name__=="__main__":
    args = get_args()
    main(args)