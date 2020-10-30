# -*- coding:utf-8 -*-
"""
@author zhangjian
"""

import os
import random
import traceback
from copy import deepcopy
from fontTools.ttLib import TTCollection, TTFont


class FontsFactory:
    def __init__(self, font_dir, fonts_prob=False):
        self.fonts_dict = self.get_all_fonts(font_dir)
        self._init_fonts_prob(fonts_prob)

    def _init_fonts_prob(self, fonts_prob):
        if fonts_prob:
            self.font_prob = fonts_prob
        else:
            # if fonts_prob not specified, use same prob for each font
            self.font_prob = {}
            for font in self.fonts_dict:
                self.font_prob[font] = 1

    def get_all_fonts(self, resource_path):
        """
        traversal the resource dir, find all font files
        """

        font_dict = {}
        all_files = os.listdir(resource_path)
        # get file end with '.ttf'
        ttf_files = list(filter(lambda x: os.path.splitext(x)[1] in ['.ttf', '.otf', '.TTF', '.ttc'], all_files))
        for ttf in ttf_files:
            charset = self.get_font_charset(os.path.join(resource_path, ttf))
            font_dict[ttf] = (os.path.join(resource_path, ttf), charset)
        return font_dict

    def _load_font(self, font_path):
        """
        Read ttc, ttf, otf font file, return a TTFont object
        """

        # ttc is collection of ttf
        if font_path.endswith('ttc'):
            ttc = TTCollection(font_path)
            # assume all ttfs in ttc file have same supported chars
            return ttc.fonts[0]

        if font_path.endswith('ttf') or font_path.endswith('TTF') or font_path.endswith('otf'):
            ttf = TTFont(font_path, 0, allowVID=0,
                         ignoreDecompileErrors=True,
                         fontNumber=-1)

            return ttf

    def get_font_charset(self, font_path):
        try:
            ttf = self._load_font(font_path)
            chars_set = set()
            for table in ttf['cmap'].tables:
                for k, v in table.cmap.items():
                    char = chr(k)
                    chars_set.add(char)
        except:
            chars_set = {}
            print(font_path+traceback.format_exc())

        return chars_set

    def get_supported_fonts(self, text):
        # drop unsupported charsets
        supported_fonts = deepcopy(self.font_prob)
        for char in text:
            for font_name in list(supported_fonts.keys()):
                if font_name in self.fonts_dict:
                    if char not in self.fonts_dict[font_name][1]:
                        supported_fonts.pop(font_name)
                else:
                    print('No such font in target dir: {}'.format(font_name))
        return supported_fonts

    def generate_font(self, text):
        # get supported fonts
        supported_fonts = self.get_supported_fonts(text)

        # randomly choose one
        if supported_fonts:
            font_name = random.choices(list(supported_fonts.keys()), list(supported_fonts.values()), k=1)[0]
            font_file = self.fonts_dict[font_name][0]
        else:
            font_name = None
            font_file = None

        return font_name, font_file


if __name__ == '__main__':
    ff = FontsFactory('/Users/Desperado/Desktop/工作文件夹/gitcode/SynthChinese/data/fonts/chn')
    print(ff.generate_font('我们'))
