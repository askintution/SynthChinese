# SynthChinese
语料合成 for OCR：根据文本语料，合成图像语料

## 1.结果示例
|(./demo/1.jpg)|(./demo/2.jpg)|
|(./demo/3.jpg)|(./demo/4.jpg)|
|(./demo/5.jpg)|(./demo/6.jpg)|
|(./demo/7.jpg)|(./demo/8.jpg)|

git clone  https://github.com/Placeboooo/SynthChinese.git
pip install requirements.txt
## 3.配置
见/configs/base.yaml
其中:
  -TEXT：文本语料相关
    -SAMPLE: 控制样本规模、文本长度、字符集等
    -CORPUS：语料目录及语料类型、权重
  -BACKGROUND：背景相关，控制背景目录，及最终语料图片的size
  -EFFECT：效果控制
    -PYGAME：控制字体及其style，作用于【font_util】
    -OPENCV: 控制透视变换、外框、模糊、噪点等，作用于【cv_util】
    -MERGE: 控制文字图像与背景的融合，作用于【merge_util】
## 4.运行
python main.py
结果：/samples/
日志：/log/
## 5.功能
### 1.语料工厂（corpus_factory）: 提供文本语料
### 2.font_util：根据字体文件将文本语料渲染成文字图像
### 3.cv_util：将文字图像进行透视变换、添加噪声...
### 4.merge_util：将文字图像与背景图像融合生成最终图像语料


