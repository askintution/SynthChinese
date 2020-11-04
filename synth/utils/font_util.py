"""
@author zhangjian
"""
import os
import random
import pygame, pygame.locals
from pygame import freetype
from synth.libs.fonts_factory import FontsFactory
from synth.libs.math_util import get_random_value

pygame.init()


class FontUtil(object):
    def __init__(self, cfg):
        """
        :param cfg:

        # cfg of font
        fonts_dir: dir of font files
        fonts: {font_short_name: font_prob,...} like {'courbd1.7': 0.5, 'courbd1.7': 0.2}

        # cfg of surface
        size: [H, W]

        # cfg of font style
        'size': size of font : [min, max, type(uniform,gaussian)]
        'oblique': prob of oblique : [prob]
        'rotation': prob of rotation and degrees range: [prob, [-360, 360,type(uniform,gaussian)]]
        'strong': : prob of strong style: [prob]
        'wide': prob of wide style: [prob]
        'strength': strength of wide and strong style: [0, 1, type(uniform,gaussian)]
        'underline': [and 'underline_adjustment']: prob of underline style and underline adjustment factor: [prob, [0, 2], type(uniform,gaussian)]
        """

        self.pygame_cfg = cfg['EFFECT']['PYGAME']
        self.font_style_cfg = self.pygame_cfg['FONT_STYLE']
        # init font factory
        self.fontFac = FontsFactory(self.pygame_cfg['FONTS']['fonts_dir'],
                                    self.pygame_cfg['FONTS']['fonts_prob'])

    def __call__(self, text):
        font_name, font_file = self.fontFac.generate_font(text)
        # size
        size = int(get_random_value(*self.font_style_cfg['size']))
        font = freetype.Font(font_file, size=int(size))
        # oblique
        if random.random() < self.font_style_cfg['oblique']:
            font.oblique = True
        # rotation
        if random.random() < self.font_style_cfg['rotation'][0]:
            degree = get_random_value(*self.font_style_cfg['rotation'][1])
            degree = int(degree)
            font.rotation = degree
        if font_name not in self.pygame_cfg['FONTS']['fonts_strong_false']:
            """
            some fonts not suitable for strong effect
            """
            # strong
            if random.random() < self.font_style_cfg['strong']:
                font.strong = True
            # wide (not supput rotated)
            if font.rotation == 0 and font.strong == False:
                if random.random() < self.font_style_cfg['wide']:
                    font.wide = True
            # strength
            if font.strong or font.wide:
                strength = get_random_value(*self.font_style_cfg['strength'])
                strength = round(strength, 2)
                font.strength = strength

        # underline (not supput rotated)
        if font.rotation == 0:
            if random.random() < self.font_style_cfg['underline'][0]:
                font.underline = True
                adj_factor = get_random_value(*self.font_style_cfg['underline'][1])
                adj_factor = round(adj_factor, 2)
                font.underline_adjustment = adj_factor

        # render to surface
        surf, rect = font.render(text)
        if rect.height <= (size * 0.6):
            # height too small like '-', use size as height
            surf = pygame.Surface((rect.width, size), pygame.locals.SRCALPHA, 32)
            font.render_to(surf, (0, int((size-rect.height)/2)), text)

        arr = pygame.surfarray.pixels_alpha(surf).swapaxes(0, 1)  # 获取图像的透明度（当render_to只传fgcolor背景就是透明的，值为0）

        # str
        font_name_str = os.path.splitext(font_name)[0]
        font_string = f'font{size}{font_name_str}_oblique{int(font.oblique)}_rotation{font.rotation}_strong{int(font.strong)}_wide{int(font.wide)}_strength{round(font.strength,2)}_underline{int(font.underline)}{font.underline_adjustment}'

        return font_string, arr

    def __str__(self):
        pass

    def play(self, FPS=5):
        import cv2
        text = '安立路319号abcDEF'

        while True:
            font_str, font_img = self.__call__(text)
            cv2.namedWindow('Play', 0)
            cv2.resizeWindow('Play', 400, 100)
            cv2.imshow('Play', 255-font_img)
            key = cv2.waitKey(int(1000/FPS))
            if key == ord('q'):
                break
            elif key == ord('s'):
                cv2.imwrite('./demo_img/'+font_str+'.jpg', 255-font_img)
        cv2.destroyAllWindows()

    def test(self, test_text, target_dir):
        import numpy as np
        import matplotlib
        import matplotlib.pyplot as plt

        #
        # suported_fonts = {'HanDingJianZhongHei-2.ttf':1 ,'MicrosoftYaqiHei-2.ttf':1}
        suported_fonts = self.fontFac.get_supported_fonts(test_text)

        # size
        sizes = [20] #np.linspace(*self.font_style_cfg['size'][0:2], 4)
        # oblique
        obliques = [False] #[True, False]
        # rotation
        rotations = [0] #[0, 10]
        # strong
        strongs = [True, False]
        # wide (not supput rotated)
        wides = [False]
        # strength
        strengths = [0.1]

        # underline (not supput rotated)
        underlines = [False] #[True, False]

        # fringe
        fringes = [0]
        # render to surface
        for font_name, _ in suported_fonts.items():
            font_file = self.fontFac.fonts_dict[font_name][0]
            for size in sizes:
                for oblique in obliques:
                    for rotation in rotations:
                        for strong in strongs:
                            for wide in wides:
                                for strength in strengths:
                                    for underline in underlines:
                                        for pixel in fringes:
                                            if pixel == 0:
                                                h = 0
                                                w = 0
                                            else:
                                                h = pixel
                                                w = pixel
                                            font = freetype.Font(font_file, size=int(size))
                                            font.oblique = oblique
                                            font.rotation = int(rotation)
                                            font.strong = strong
                                            if font.rotation == 0:
                                                font.wide = wide
                                                font.underline = underline
                                            font.strength = strength

                                            rect = font.get_rect(test_text)
                                            surf = pygame.Surface((rect.width, rect.height), pygame.locals.SRCALPHA, 32)
                                            font.render_to(surf, (0, 0), test_text)

                                            if pixel > 0:
                                                font.render_to(surf, (pixel, pixel), test_text)

                                            arr = pygame.surfarray.pixels_alpha(surf).swapaxes(0, 1)  # 获取图像的透明度（当render_to只传fgcolor背景就是透明的，值为0）

                                            # str
                                            font_name_str = os.path.splitext(font_name)[0]
                                            font_string = f'font{size}{font_name_str}_oblique{int(font.oblique)}_rotation{font.rotation}_strong{int(font.strong)}_wide{int(font.wide)}_strength{round(font.strength,2)}_underline{int(font.underline)}{font.underline_adjustment}_fringe{round(h,1)}-{round(w,1)}'
                                            plt.figure(font_string)
                                            plt.imshow(255 - arr, cmap='gray')
                                            plt.savefig(os.path.join(target_dir, font_string + '.jpeg'))
                                            plt.close()


if __name__ == '__main__':
    import yaml

    cfg = yaml.load(open('../../configs/base.yaml', encoding='utf-8'), Loader=yaml.FullLoader)
    cfg['EFFECT']['PYGAME']['FONTS']['fonts_dir'] = '../../data/fonts'
    FU = FontUtil(cfg)
    FU.play(3)
