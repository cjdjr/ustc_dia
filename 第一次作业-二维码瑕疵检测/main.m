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

%% ����ڶ�ֵͼ��bw������ά��覴����������
% ���Ե��õĺ�����im2bw, bwlabel, bwmorph, regionprops�������в��ĺ���˵��


