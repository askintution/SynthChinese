# -*- coding:utf-8 -*-
"""
@author zhangjian
"""

import os
import cv2
import random
import numpy as np


class bgFactory:

    def __init__(self, backgroud_dir, height=32, width=400):
        self.all_bgs = self.get_bgs(backgroud_dir)
        self.bgs_keys = list(self.all_bgs.keys())
        self.defaut_height = height
        self.defaut_width = width

    def get_bgs(self, bgs_dir):
        all_imgs = {}
        if os.path.exists(bgs_dir):
            all_files = os.listdir(bgs_dir)
            pic_files = list(filter(lambda x: os.path.splitext(x)[1] in ['.jpg', '.jpeg', '.png'], all_files))

            for fname in pic_files:
                bg = cv2.imread(os.path.join(bgs_dir, fname))
                bg_name = os.path.splitext(fname)[0].replace('_', '')
                all_imgs[bg_name] = bg
        return all_imgs

    def getnerate_bg(self, height=None, width=None, rgb=False):
        if height is None or width is None:
            height = self.defaut_height
            width = self.defaut_width
        bg_name = random.choice(self.bgs_keys)
        bg_img = self.all_bgs[bg_name]
        # check shape and resize
        h, w = bg_img.shape[0:2]
        if w < width or h < height:
            w1, h1 = int(w * height / h), height
            w2, h2 = width, int(h * width / w)
            if w1 >= width and h1 >= width:
                bg_img = cv2.resize(bg_img, (w1, h1), interpolation=cv2.INTER_AREA)
            else:
                bg_img = cv2.resize(bg_img, (w2, h2), interpolation=cv2.INTER_AREA)
        # random crop
        h, w = bg_img.shape[0:2]
        x = random.randint(0, w - width)
        y = random.randint(0, h - height)
        cropped_img = bg_img[y:y + height, x:x + width, :]
        # rgb
        if not rgb:
            cropped_img = cv2.cvtColor(cropped_img,  cv2.COLOR_BGR2GRAY)
            cropped_img = np.expand_dims(cropped_img, 2)
        return bg_name, cropped_img

    def play(self, FPS=5):
        while True:
            bg_name, bg_img = self.getnerate_bg(rgb=True)
            cv2.imshow('Play', bg_img)
            key = cv2.waitKey(int(1000/FPS))
            if key == ord('q'):
                break
        cv2.destroyAllWindows()


if __name__ == '__main__':
    bgf = bgFactory('../../data/background')
    # bgf.play()
    cv2.imshow('test', bgf.all_bgs['bg2'])
    _,img2 = bgf.getnerate_bg(rgb=False)
    cv2.imshow('test1', img2)

