# -*- coding:utf-8 -*-
"""
@author zhangjian
"""
import cv2
import os
import random
import numpy as np
from synth.libs.math_util import PerspectiveTransform, get_random_value


class cvUtil(object):
    def __init__(self, cfg):
        """
        :param cfg:

        'perspective': cv2.getPerspectiveTransform
        'blur':􏰛􏰜􏰝􏰞􏴍􏰎􏲓􏱾􏰃􏴓􏴗􏴗􏳕􏰃􏰄􏵣􏰎􏴎􏰄􏰎􏱲􏰟􏰠 􏰛􏰜􏰝􏰞􏱾􏰃􏴓􏴗􏴗􏳕􏰃􏰄􏳬􏱲􏴓􏴎􏰟􏰠cv2.􏰛􏰜􏰝􏰞􏱾􏰃􏴓􏴗􏴗􏳕􏰃􏰄􏳬􏱲􏴓􏴎􏰟􏰠GuassianBlur
        'erosion': 􏰛􏰜􏰝􏰞􏰎􏴎􏰮􏴏􏰎􏰛􏰜􏰝􏰞􏰎􏴎􏰮􏴏􏰎cv2.erode
        'box': drabox

        """
        self.open_cv_conf = cfg['EFFECT']['OPENCV']
        self.create_kernals()

    def warpPerspectiveTransform(self, img, x, y, z):
        """
        执行透视变换，并裁取变换后的文字区域
        """
        raw_h, raw_w = img.shape
        transformer = PerspectiveTransform(x, y, z, scale=1.0, fovy=50)
        dst_img, M33, dst_img_pnts = transformer.transform_image(img)
        x, y, w, h = cv2.boundingRect(dst_img)  # 获取文本边界
        new_img = dst_img[y:y + h, x:x + w]
        # 尺寸还原，保持长宽比缩放，两边都不超过原尺寸
        new_h, new_w = new_img.shape
        w1, h1 = int(new_w * raw_h / new_h), raw_h
        w2, h2 = raw_w, int(new_h * raw_w / new_w)
        if w1 <= raw_w and h1 <= raw_h:
            new_img = cv2.resize(new_img, (w1, h1), interpolation=cv2.INTER_AREA)
        else:
            new_img = cv2.resize(new_img, (w2, h2), interpolation=cv2.INTER_AREA)
        return new_img

    def draw_box(self, img, alpha=1.3):
        """
        先将图片pad为原尺寸的4/3，画框，再resize回原尺寸
        """
        h, w = img.shape
        dst_h, dst_w = int(h * alpha), int(w * alpha)
        top = random.randint(1, dst_h - h - 1)
        bottom = dst_h - h - top
        left = random.randint(1, dst_w - w - 1)
        right = dst_w - w - left
        img_new = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT,
                                     value=0)  # top,bottom,left,right

        # draw_box
        left_top = (random.randint(0, left), random.randint(0, top))
        right_bottom = (random.randint(dst_w-right, dst_w), random.randint(dst_h-bottom, dst_h))
        cv2.rectangle(img_new, left_top, right_bottom, 255, random.randint(1, 2))
        img_new = cv2.resize(img_new, (w, h), interpolation=cv2.INTER_AREA)
        return img_new

    def gauss_blur(self, img, ksize, sigma):
        img = cv2.GaussianBlur(img, (ksize, ksize), sigma)
        return img

    def apply_prydown(self, img):
        """
        模糊图像，模拟小图片放大的效果
        """
        scale = random.uniform(1, 2)
        height = img.shape[0]
        width = img.shape[1]

        out = cv2.resize(img, (int(width / scale), int(height / scale)), interpolation=cv2.INTER_AREA)
        return cv2.resize(out, (width, height), interpolation=cv2.INTER_AREA)

    def create_kernals(self):
        self.emboss_kernal = np.array([
            [-2, -1, 0],
            [-1, 1, 1],
            [0, 1, 2]
        ])

        self.sharp_kernel = np.array([
            [-1, -1, -1],
            [-1, 9, -1],
            [-1, -1, -1]
        ])

    def apply_emboss(self, word_img):
        return cv2.filter2D(word_img, -1, self.emboss_kernal)

    def apply_sharp(self, word_img):
        return cv2.filter2D(word_img, -1, self.sharp_kernel)

    def __call__(self, img):

        cv_str = ''
        # box
        if random.random() < self.open_cv_conf['BOX']:
            img = self.draw_box(img)
            cv_str += '_box'
        # warp
        if random.random() < self.open_cv_conf['PERSPECTIVE']:
            X = get_random_value(*self.open_cv_conf['PERSPECTIVE_X'])
            Y = get_random_value(*self.open_cv_conf['PERSPECTIVE_Y'])
            Z = get_random_value(*self.open_cv_conf['PERSPECTIVE_Z'])
            img = self.warpPerspectiveTransform(img, X, Y, Z)
            cv_str += '_warp_{}_{}_{}'.format(int(X), int(Y), int(Z))
        # blur
        if random.random() < self.open_cv_conf['BLUR']:
            ksize = random.choice(self.open_cv_conf['BLUR_KSIZE'])
            sigma = random.choice(self.open_cv_conf['BLUR_SIGMA'])
            if ksize > 3:
                sigma = 1
            img = self.gauss_blur(img, ksize, sigma)
            cv_str += '_blur_{}_{}'.format(ksize, sigma)
            # emboss
            if random.random() < self.open_cv_conf['FILTER'][0]:
                if random.random() < self.open_cv_conf['FILTER'][1][0]:
                    img = self.apply_emboss(img)
                    cv_str += '_emboss'
                else:
                    img = self.apply_sharp(img)
                    cv_str += '_sharp'
        if cv_str:
            pass
        else:
            cv_str = 'N'
        return cv_str, img

    def play(self, FPS=5):
        img = cv2.imread('./demo_img/font_img_1.jpg', cv2.IMREAD_GRAYSCALE)
        while True:
            cv_name, cv_img = self.__call__(img)
            cv2.namedWindow('Play', 0)
            cv2.resizeWindow('Play', 400, 100)
            cv2.imshow('Play', cv_img)
            key = cv2.waitKey(int(1000/FPS))
            if key == ord('q'):
                break
        cv2.destroyAllWindows()

    def test(self, font_util, test_text, target_dir):

        import matplotlib
        import matplotlib.pyplot as plt

        # 原始
        font_string, arr = font_util(test_text)
        plt.figure(font_string)
        plt.imshow(255 - arr, cmap='gray')
        plt.savefig(os.path.join(target_dir, font_string + '原.jpeg'))
        print(arr.shape)
        # box
        arr = self.draw_box(arr)
        plt.figure(font_string + 'box')
        plt.imshow(255 - arr, cmap='gray')
        plt.savefig(os.path.join(target_dir, font_string + 'box.jpeg'))
        print(arr.shape)
        # warp
        arr = self.warpPerspectiveTransform(arr, -8, 0, 0)
        plt.figure(font_string + 'warp')
        plt.imshow(255 - arr, cmap='gray')
        plt.savefig(os.path.join(target_dir, font_string + 'box_warp.jpeg'))
        print(arr.shape)
        # blur
        arr = self.gauss_blur(arr, 3, 7)
        plt.figure(font_string + 'blur')
        plt.imshow(255 - arr, cmap='gray')
        plt.savefig(os.path.join(target_dir, font_string + 'box_warp_blur.jpeg'))
        # emboss
        arr1 = self.apply_emboss(arr)
        plt.figure(font_string + 'emboss')
        plt.imshow(255 - arr1, cmap='gray')
        plt.savefig(os.path.join(target_dir, font_string + 'box_warp_blur_emboss.jpeg'))
        # sharp
        arr2 = self.apply_sharp(arr1)
        plt.figure(font_string + 'sharp')
        plt.imshow(255 - arr2, cmap='gray')
        plt.savefig(os.path.join(target_dir, font_string + 'box_warp_blur_sharp.jpeg'))

        #plt.close()
        return arr


if __name__ == '__main__':
    import yaml

    cfg = yaml.load(open('../../configs/base.yaml', encoding='utf-8'), Loader=yaml.FullLoader)
    cv_util = cvUtil(cfg)
    cv_util.play()