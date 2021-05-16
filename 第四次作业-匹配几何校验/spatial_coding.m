%% Set path and parameters
clear;
close all;
clc;

% src_1 = './test_images/Mona-Lisa-73.jpg';  
% src_2 = './test_images/Mona-Lisa-452.jpg';

src_1 = './test_images/4.jpg';  
src_2 = './test_images/Disney-00558.jpg';


ext = '.sift';  % extension name of SIFT file
siftDim = 128;
maxAxis = 400;


%%  Load image
im_1 = imread(src_1);
if max(size(im_1)) > maxAxis
    im_1 = imresize(im_1, maxAxis / max(size(im_1)));
end

im_2 = imread(src_2);
if max(size(im_2)) > maxAxis
    im_2 = imresize(im_2, maxAxis / max(size(im_2)));
end


%%  Load SIFT feature from file
featPath_1 = [src_1, ext];
featPath_2 = [src_2, ext];

fid_1 = fopen(featPath_1, 'rb');
featNum_1 = fread(fid_1, 1, 'int32');
SiftFeat_1 = zeros(siftDim, featNum_1);
paraFeat_1 = zeros(4, featNum_1);
for i = 1 : featNum_1
    SiftFeat_1(:, i) = fread(fid_1, siftDim, 'uchar');
    paraFeat_1(:, i) = fread(fid_1, 4, 'float32');
end
fclose(fid_1);

fid_2 = fopen(featPath_2, 'rb');
featNum_2 = fread(fid_2, 1, 'int32');
SiftFeat_2 = zeros(siftDim, featNum_2);
paraFeat_2 = zeros(4, featNum_2);
for i = 1 : featNum_2
    SiftFeat_2(:, i) = fread(fid_2, siftDim, 'uchar');
    paraFeat_2(:, i) = fread(fid_2, 4, 'float32');
end
fclose(fid_1);


%% Normalization
SiftFeat_1 = SiftFeat_1 ./ repmat(sqrt(sum(SiftFeat_1.^2)), size(SiftFeat_1, 1), 1);
SiftFeat_2 = SiftFeat_2 ./ repmat(sqrt(sum(SiftFeat_2.^2)), size(SiftFeat_2, 1), 1);


%% Check match based on distances between SIFT descriptors across images
normVal = mean(sqrt(sum(SiftFeat_1.^2)));
matchInd = zeros(featNum_1, 1);
matchDis = zeros(featNum_1, 1);
validDis = [];
gridDisVec = [];
ic = 0;
for i = 1 : featNum_1  % 以第一张图描述子数量为基准进行匹配
    tmpFeat = repmat(SiftFeat_1(:, i), 1, featNum_2);  % repmat(A,m,n)，将矩阵 A 复制 m×n 块，即128*featNum_2
    d = sqrt(sum((tmpFeat - SiftFeat_2).^2)) / normVal;  % L2 distance，图1第i个描述子与图2所有描述子的距离向量
    matchDis(i) = min(d);
    [v, ind] = sort(d);
    if v(1) < 0.4  % 最小距离小于0.4，则认为构成一对匹配
        matchInd(i) = ind(1);
        ic = ic + 1;
        validDis(ic, 1 : 3) = [v(1), v(2), v(1) / v(2)];
        tmp = (SiftFeat_1(:, i) - SiftFeat_2(:, ind(1))).^2;
        tmp2 = reshape(tmp(:), 8, 16);
        gridDisVec(ic, 1 : 16) = sqrt(sum(tmp2));  % 第ic个匹配描述子的L2距离
    end
end
figure; stem(matchDis); ylim([0, 1.2]);  % 绘制茎状图
figure; stem(matchDis(matchInd > 0)); ylim([0, 1.2]);

%% 实现spatial coding方法，进行匹配校验准备
Map1 = [];
Map2 = [];
m= 1;
for i = 1 : featNum_1
    if matchInd(i) > 0
        Map1 = [Map1, paraFeat_1(1:2, i)];
        Map2 = [Map2, paraFeat_2(1:2, matchInd(i))];
    end
end

r = 4;    
GX1(ic, ic, r) = 0;
GY1(ic, ic, r) = 0;
GX2(ic, ic, r) = 0;
GY2(ic, ic, r) = 0;
for k = 1:r
    %% 将其分解为r个独立的子区域，旋转k个单位的坐标集
    theta = (k-1)*pi/(2*r);
    G1(1:2, 1:ic, k) = [cos(theta), -sin(theta); sin(theta), cos(theta)]*Map1;
    G2(1:2, 1:ic, k) = [cos(theta), -sin(theta); sin(theta), cos(theta)]*Map2;
    %% 获取空间编码01矩阵
    for i = 1:ic
        for j = 1:ic
            if G1(1, i, k) >= G1(1, j, k) 
                GX1(j, i, k) = 1;
            end
            if G1(2, i, k) >= G1(2, j, k) 
                GY1(i, j, k) = 1;
            end
            if G2(1, i, k) >= G2(1, j, k) 
                GX2(j, i, k) = 1;
            end
            if G2(2, i, k) >= G2(2, j, k) 
                GY2(i, j, k) = 1;
            end
        end
    end
end
Vx = xor(GX1, GX2);
Vy = xor(GY1, GY2);

%% Show the local matching results on RGB image
[row, col, cn] = size(im_1);
[r2, c2, n2] = size(im_2);
imgBig = 255 * ones(max(row, r2), col + c2, 3);
imgBig(1 : row, 1 : col, :) = im_1;
imgBig(1 : r2, col + 1 : end, :) = im_2;
paraFeat_2(1, :) = paraFeat_2(1, :) + col;      %为了让两幅图画面并排，使右侧图x坐标右移col个单位
figure(3); imshow(uint8(imgBig)); axis on;
hold on;
matchCount = 0;
for i = 1 : featNum_1
    if matchInd(i) > 0
        matchCount = matchCount + 1;
        xys = paraFeat_1(:, i);
        xys2 = paraFeat_2(:, matchInd(i));
        figure(3);
        hold on; 
        plot([xys(1), xys2(1)], [xys(2), xys2(2)], '-b', 'LineWidth', 0.8);  % 匹配点连线
    end
end

%% 几何匹配校验
Map2(1, :) = Map2(1, :) + col;  % 为了让两幅图画面并排，使右侧图x坐标右移col个单位
threshold = floor(ic*0.8);
for i = 1:ic
    Sx = sum(sum(Vx, 2), 3);  % 矩阵各行元素求和，再对k个方向各行元素和求总和
    [Cx, Ix] = max(Sx(:, :), [], 1);  % 求出第k个方向的列最大值
    if Cx>threshold
        Vx(Ix, :, :) = 0;  % 把最不匹配的描述子mask
        Vx(:, Ix, :) = 0;
        Vy(Ix, :, :) = 0;  % 把最不匹配的描述子mask
        Vy(:, Ix, :) = 0;
        hold on;
        plot([Map1(1, Ix), Map2(1, Ix)], [Map1(2, Ix), Map2(2, Ix)], '-r', 'LineWidth', 0.8);  % 不匹配的描述点对连线
    end
    Sy = sum(sum(Vy, 2), 3);  % 矩阵对各行元素求和
    [Cy, Iy] = max(Sy(:, :), [], 1);
    if Cy>threshold
        Vx(Iy, :, :) = 0;  % 把最不匹配的描述子mask
        Vx(:, Iy, :) = 0;
        Vy(Iy, :, :) = 0;  % 把最不匹配的描述子mask
        Vy(:, Iy, :) = 0;
        hold on;plot([Map1(1, Iy), Map2(1, Iy)], [Map1(2, Iy), Map2(2, Iy)], '-r', 'LineWidth', 0.8);  % 不匹配的描述点对连线
    end
end
figure(3);
title(sprintf('Total local matches : %d (%d-%d)', length(find(matchInd)), featNum_1 ,featNum_2));
hold off;