# SynthChinese
OCR语料合成：根据文本语料合成图像语料

## 1.结果示例
![1.jpg](./demo/1.jpg)
![2.jpg](./demo/2.jpg)
![3.jpg](./demo/3.jpg)
![4.jpg](./demo/4.jpg)
![5.jpg](./demo/5.jpg)
![6.jpg](./demo/6.jpg)
![7.jpg](./demo/7.jpg)
![8.jpg](./demo/8.jpg)
### 效果列表（非全部）
|效果名称|所在模块|备注|
|--------|-----|-------|
|font|font_util|随机选择字体|
|oblique|font_util|倾斜|
|rotation|font_util|旋转|
|strong|font_util|加粗|
|wide|font_util|加宽|
|underline|font_util|下划线|
|box|cv_util|加外框|
|perspective|cv_util|透视变换|
|blur|cv_util|高斯模糊|
|filter|cv_util|emboss或sharp滤波|
|crop|merge_util|背景随机剪裁|
|color|merge_util|随机调整亮度和对比度|
|reverse|merge_util|反转颜色|
|noise|merge_util|噪点（4种类型）|


## 2.安装
git clone  https://github.com/Placeboooo/SynthChinese.git  
pip install requirements.txt
## 3.配置
<p>
见/configs/base.yaml  
  
  
其中:  
-TEXT：文本语料相关  
---SAMPLE: 控制样本规模、文本长度、字符集等  
---CORPUS：语料目录及语料类型、权重  
-BACKGROUND：背景相关，控制背景目录，及最终语料图片的size  
-EFFECT：效果控制  
---PYGAME：控制字体及其style，作用于【font_util】  
---OPENCV: 控制透视变换、外框、模糊、噪点等，作用于【cv_util】  
---MERGE: 控制文字图像与背景的融合，作用于【merge_util】
<p>
      
## 4.运行
python main.py  
结果：/samples/  
日志：/log/  

## 5.功能
### 1.语料工厂（synth.corpus.corpus_factory）: 提供文本语料
该模块提供了提供文本语料的功能。  
其中，base_render.py可以指定语料目录，及语料的类型及权重  
     date_render.py则可以模拟生成日期类语料  
     id_render.py随机生成身份证号语料  
     ...  
你也可以根据自己的任务写新的render，将其加入到base_corpus_factory.py中即可  
### 2.font_util（）：根据字体文件将文本语料渲染成文字图像  
该模块使用pygame模块将文本渲染成为图像。
其中，fontfactory模块会检查文本语料支持的字体，并根据指定的概率随机选取字体（如不指定则概率相同）  
然后，根据配置的概率随机设定文字效果  
最后，返回效果字符串和渲染的图像。  
你可以调用该模块的play功能调试不同配置产生的字体效果。  
### 3.cv_util：将文字图像进行透视变换、添加噪声...
该模块调用opencv为文字图像添加变化。  
其中包含的功能大致有：透视变换（可以定义图像在x、y、z轴翻转的角度）、文字外框、高斯模糊、emboss filter、sharp filter  
同样，你可以调用该模块的play功能调试不同配置产生的效果。  
### 4.merge_util：将文字图像与背景图像融合生成最终图像语料
该模块将文字图像与背景图像融合，产生最终的图片语料。  
其中，背景部分调用bg_factory，使用从背景资源中随机选取一张背景，并随机裁取指定尺寸的图像作为文字背景。  
然后，随机调整背景及文字图像的亮度和对比度，并通过泊松编辑将文字图像和背景图像融合  
最后，随机为图像增加四种类型的噪点  
同样，你可以调用该模块的play功能调试不同配置产生的效果。




