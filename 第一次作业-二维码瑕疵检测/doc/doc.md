# 二维码瑕疵检测

**汪敏瑞**

**SA2006150**



## 1. 任务描述

一维条码中可能存在的断码、白点、黑点等影响条码外观的瑕疵，检测这些瑕疵，并用红色矩形框将其标出。



## 2. 方法



观察到图片中的二维码基本是由近乎垂直的细线段组成的，所以可以先根据sobel算子计算梯度，突出垂直方向的边缘信息，淡化其他区域的干扰信息，然后将图像二值化。接下来，将二值化后的图像生成最小外接矩形，并取面积最大的两个区域认为它们就表示两个二维码区域。由于二维码区域可能有略微的倾斜，于是再根据最小外接矩形的角度对原图像进行旋转矫正。对于矫正后的每个二维码区域，进行形态学上的腐蚀操作，补全缺少的二维码信息，再与原图二维码区域相减，于是暴露出瑕疵区域，最后再用最小外接矩形把这些瑕疵区域框出来。



### 2.1 图像预处理

将原来的彩色图像转成灰度图，过高斯滤波平滑噪声之后计算横纵方向的sobel算子，求得梯度图（由于二维码线段由很细的垂直线段组成，所以这样的梯度图可以完整地保留二维码信息，同时可以忽略到一些其他区域地干扰信息）。对梯度图进行二值化，完成图像预处理步骤。

 <center>
    <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416194445662.png" width = "30%" alt=""/>
    <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416194538818.png" width = "30%" alt=""/>
    <br>
    <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">
      图1  左图是原图，右图是预处理之后的图。
  	</div>
</center>



### 2.2 获取二维码区域

对上步得到的二值化处理后的图像，取$50 \times 10$的长条作为结构元素，进行闭运算，将二维码区域整合成完整的区域。然后进行开运算，目的是去除孤立的前景区域。然后寻找面积最大的两个最小外接矩形就能确定两个二维码区域。

 <center>
    <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416220256881.png" width = "30%" alt=""/>
    <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416220317614.png" width = "30%" alt=""/>
    <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416220344522.png" width = "30%" alt=""/>
    <br>
    <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">
      图2  左图是二值化后的图像，中间是经过闭运算得到的图像，右边是经过开运算的到的图像。
  	</div>
</center>



### 2.3 旋转矫正图像

根据得到的最小外接矩形，确定矫正图像的旋转角度，将原图和二值化后的图像都按照该角度进行旋转矫正。



### 2.4 检测二维码瑕疵区域

在经旋转矫正后的原图的二维码区域进行腐蚀操作，由于二维码的黑色条纹的像素值比背景白色的像素值小，所以可以补充二维码黑色线条断裂处。然后将补充之后的图像与补充之前的图像相减，就可以知道补充的位置像素（瑕疵处），再寻找最小外接矩形将瑕疵处框住即可。

 <center>
    <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416221522347.png" width = "70%" alt=""/>
</center>



 <center>
    <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416221556248.png" width = "70%" alt=""/>
</center>



 <center>
    <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416221621990.png" width = "70%" alt=""/>
    <br>
</center>


<center>
    <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">
      图3  上图是原始图像，中间是经过腐蚀后的图像，下面是检测出来的瑕疵处。
  	</div>
</center>



## 3. 实验结果

 <center>
  <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416222547927.png" width = "50%" alt=""/>
  <br>
  <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">
      图4  barcode_1_result
  </div>
</center>

 <center>
  <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416222815044.png" width = "50%" alt=""/>
  <br>
  <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">
      图5  barcode_3_result
  </div>
</center>

 <center>
  <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416222943197.png" width = "50%" alt=""/>
  <br>
  <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">
      图6  barcode_4_result
  </div>
</center>

 <center>
  <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416223010502.png" width = "50%" alt=""/>
  <br>
  <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">
      图7  barcode_6_result
  </div>
</center>

 <center>
  <img style="border-radius: 0.3125em;
    box-shadow: 0 2px 4px 0 rgba(34,36,38,.12),0 2px 10px 0 rgba(34,36,38,.08);" 
    src="C:\Users\chelly\AppData\Roaming\Typora\typora-user-images\image-20210416223031920.png" width = "50%" alt=""/>
  <br>
  <div style="color:orange; border-bottom: 1px solid #d9d9d9;
    display: inline-block;
    color: #999;
    padding: 2px;">
      图8  barcode_7_result
  </div>
</center>

