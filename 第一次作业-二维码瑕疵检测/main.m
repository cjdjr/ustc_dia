clear; 
close all;
clc;

%% Binarize the input image
im = imread('test images/barcode_1.png');

im_gray = rgb2gray(im);
level = graythresh(im_gray);
bw = im2bw(im_gray, level);

figure; 
subplot(2, 1, 1); imshow(im_gray); title('original image');
subplot(2, 1, 2); imshow(bw); title('binary result');

%% 请基于二值图像bw，将二维码瑕疵区域检测出来
% 可以调用的函数：im2bw, bwlabel, bwmorph, regionprops，请自行查阅函数说明


