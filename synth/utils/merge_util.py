# -*- coding:utf-8 -*-
"""
@author zhangjian
"""
import cv2
import random
import numpy as np
from synth.libs.bg_factory import bgFactory
from synth.libs.poisson_reconstruct import blit_images
from synth.libs.math_util import get_random_value


class MergeUtil(object):
    def __init__(self, cfg):
        """
        """
        self.merge_cfg = cfg['EFFECT']['MERGE']
        self.bg_factory = bgFactory(cfg['BACKGROUND']['DIR'], *cfg['BACKGROUND']['SIZE'])

    def random_pad(self, font_img, bg_shape):
        """
        pad font image to same size with background image
        """
        # resize
        h, w = font_img.shape[:2]
        if h < 10:  # 因对“-”等符号的高度过小
            text_mask = np.pad(font_img, ((10 - h, 10 - h), (0, 0)), 'constant')
            h, w = text_mask.shape[:2]

        resize_h = bg_shape[0] - int(random.uniform(2, self.merge_cfg['max_height_diff']))  # 比背景少2到n个像素
        resize_w = np.clip(int(w * resize_h / float(h)), 1, bg_shape[1])  # 按比例缩放，最大不能超过bg_w
        font_img = cv2.resize(font_img, (resize_w, resize_h), interpolation=cv2.INTER_CUBIC)
        # random pad
        h, w = font_img.shape[:2]
        top_padding = int(random.uniform(0, bg_shape[0] - h))
        left_padding = int(random.uniform(0, bg_shape[1] - w))
        down_padding = bg_shape[0] - (top_padding + h)
        right_padding = bg_shape[1] - (left_padding + w)
        text_arr = np.pad(font_img, ((top_padding, down_padding), (left_padding, right_padding)), 'constant')
        return text_arr

    def get_font_color(self, bg_img):
        """
        文字的最大亮度为背景均值的max_ratio倍，如2/3
        """
        word_color_max = int(np.mean(bg_img) * self.merge_cfg['max_ratio'])
        word_color = random.randint(0, word_color_max)
        return word_color

    def random_change_bgcolor(self, bg_img):
        """
        随机调节背景图片的亮度和对比度
        调节因子为 a*f(x)+b, 其中a:[0.7, 1.4], b:[-50, 50]
        """
        bg_img = bg_img.astype(np.int)
        a = get_random_value(*self.merge_cfg['alpha'])
        b = get_random_value(*self.merge_cfg['beta'])
        new_bg_img = bg_img * a + b
        new_bg_img = np.clip(new_bg_img, 50, 255)
        return new_bg_img.astype(np.uint8)

    def poisson_edit(self, font_img, bg_img):
        """
        泊松编辑，使文字图像（font_img）和背景图像（bg_img）更好的融合
        :param font_img: 文字图片
        :param bg_img: 背景
        :return:
        """
        # 将文字图随机pad到同背景同样大小
        padded_font_img = self.random_pad(font_img, bg_img.shape)
        # 随机调整背景亮度
        bg_img = self.random_change_bgcolor(bg_img)
        # 随机调整文字图亮度
        font_color = self.get_font_color(bg_img)
        dark_ratio = (255-font_color) / 255
        adj_font_img = padded_font_img * dark_ratio
        # 将文字图反转（pygame_util产生的是反的）
        reversed_font_img = 255 - adj_font_img
        # 泊松编辑
        final_img = blit_images(reversed_font_img, bg_img)
        # 随机颜色翻转
        if random.random() < self.merge_cfg['reverse']:
            final_img = 255 - final_img
            dark_ratio = 1. / dark_ratio
        merge_str = f'bgc{int(np.mean(bg_img))}_dr{round(dark_ratio,2)}'
        return merge_str, final_img

    def apply_gauss_noise(self, img):
        """
        Gaussian-distributed additive noise.
        """
        mean = 0
        stddev = np.sqrt(15)
        gauss_noise = np.zeros(img.shape)
        cv2.randn(gauss_noise, mean, stddev)
        out = img + gauss_noise

        return out

    def apply_uniform_noise(self, img):
        """
        Apply zero-mean uniform noise
        """
        imshape = img.shape
        alpha = 0.05
        gauss = np.random.uniform(0 - alpha, alpha, imshape)
        gauss = gauss.reshape(*imshape)
        out = img + img * gauss
        return out

    def apply_sp_noise(self, img):
        """
        Salt and pepper noise. Replaces random pixels with 0 or 255.
        """
        s_vs_p = 0.5
        amount = np.random.uniform(0.004, 0.01)
        out = np.copy(img)
        # Salt mode
        num_salt = np.ceil(amount * img.size * s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt))
                  for i in img.shape]
        out[tuple(coords)] = 255

        # Pepper mode
        num_pepper = np.ceil(amount * img.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper))
                  for i in img.shape]
        out[tuple(coords)] = 0
        return out

    def apply_poisson_noise(self, img):
        """
        Poisson-distributed noise generated from the data.
        """
        vals = len(np.unique(img))
        vals = 2 ** np.ceil(np.log2(vals))

        if vals < 0:
            return img

        noisy = np.random.poisson(img * vals) / float(vals)
        return noisy

    def __call__(self, font_img):
        """
        """
        # generate bg
        bg_name, bg_img =self.bg_factory.getnerate_bg()
        # merge font_img and bg_img
        merge_str, merged_img = self.poisson_edit(font_img, bg_img)
        bg_name += f'_{merge_str}'
        # add noise
        if random.random() < self.merge_cfg['NOISE']:
            all_type = self.merge_cfg['NOISE_TYPE']
            noise_type = random.choices(list(all_type.keys()), list(all_type.values()), k=1)[0]
            if noise_type == 'gauss':
                final_img = self.apply_gauss_noise(merged_img)
            elif noise_type == 'uniform':
                final_img = self.apply_uniform_noise(merged_img)
            elif noise_type == 'saltpepper':
                final_img = self.apply_sp_noise(merged_img)
            elif noise_type == 'poisson':
                final_img = self.apply_poisson_noise(merged_img)
            else:
                print(f'NOISE TYPE ERROR:{noise_type}')
                final_img = merged_img
            bg_name += f'_{noise_type}'

        else:
            final_img = merged_img

        return bg_name, final_img

    def play(self, FPS=5):
        font_img = 255-cv2.imread('./demo_img/font_img_1.jpg', cv2.IMREAD_GRAYSCALE)
        self.bg_factory = bgFactory('../../data/background')
        while True:
            final_str, final_img = self.__call__(font_img)
            cv2.namedWindow('Play', 0)
            cv2.resizeWindow('Play', 400, 100)
            cv2.imshow('Play', final_img)
            key = cv2.waitKey(int(1000 / FPS))
            if key == ord('q'):
                break

            # cv2.imwrite('/Users/Desperado/Desktop/工作文件夹/gitcode/SynthChinese/samples/'+final_str+'.jpg', final_img)
        cv2.destroyAllWindows()


if __name__ == '__main__':
    import yaml
    import matplotlib
    import matplotlib.pyplot as plt
    from synth.utils.font_util import FontUtil
    from synth.utils.cv_util import cvUtil
    from synth.libs.bg_factory import bgFactory

    cfg = yaml.load(open('/Users/Desperado/Desktop/工作文件夹/gitcode/SynthChinese/configs/test.yaml', encoding='utf-8'),
                    Loader=yaml.FullLoader)

    font_util = FontUtil(cfg)
    cv_util = cvUtil(cfg)
    # a = cv_util.test(font_util, '安立路319号', '/Users/Desperado/Desktop/工作文件夹/gitcode/SynthChinese/samples')
    text = '安立路319号'
    font_str, img = font_util(text)
    cv_str, img = cv_util(img)


    merge_util = MergeUtil(cfg)
    merge_util.play()
    #final = merge_util(img,  bg_img)
    # plt.figure(font_str + cv_str)
    # plt.imshow(final, cmap='gray')
    # plt.savefig(os.path.join(font_str+cv_str + '.jpeg'))
    # cv2.imwrite('/Users/Desperado/Desktop/工作文件夹/gitcode/SynthChinese/samples/1.jpg', final)
    # cv2.imshow('a', final)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

