#!/usr/env/bin python3
from functools import reduce
import numpy as np
import cv2
import math
import random


# http://planning.cs.uiuc.edu/node102.html
def get_rotate_matrix(x, y, z):
    """
    按照 zyx 的顺序旋转，输入角度单位为 degrees, 均为顺时针旋转
    :param x: X-axis
    :param y: Y-axis
    :param z: Z-axis
    :return:
    """
    x = math.radians(x)
    y = math.radians(y)
    z = math.radians(z)

    c, s = math.cos(y), math.sin(y)
    M_y = np.matrix([[c, 0., s, 0.],
                     [0., 1., 0., 0.],
                     [-s, 0., c, 0.],
                     [0., 0., 0., 1.]])

    c, s = math.cos(x), math.sin(x)
    M_x = np.matrix([[1., 0., 0., 0.],
                     [0., c, -s, 0.],
                     [0., s, c, 0.],
                     [0., 0., 0., 1.]])

    c, s = math.cos(z), math.sin(z)
    M_z = np.matrix([[c, -s, 0., 0.],
                     [s, c, 0., 0.],
                     [0., 0., 1., 0.],
                     [0., 0., 0., 1.]])

    return M_x * M_y * M_z


def scaled_gaussian(min_val, max_val):
    """
    1. make sure 99.7% value in [min, max]
    2. when value out of range, scale it

    """
    u = (max_val + min_val) / 2
    sigma = (max_val - min_val) / 6
    val = random.gauss(u, sigma)
    if val < min_val:
        return min_val
    if val > max_val:
        return max_val
    return val

def get_random_value(min_val, max_val, random_type):
    if random_type == 'gaussian':
        return scaled_gaussian(min_val, max_val)
    else:
        return random.uniform(min_val, max_val)


def warpPerspective(src, M33, sl):
    dst = cv2.warpPerspective(src, M33, (sl, sl), flags=cv2.INTER_CUBIC)
    return dst


# https://stackoverflow.com/questions/17087446/how-to-calculate-perspective-transform-for-opencv-from-rotation-angles
# https://nbviewer.jupyter.org/github/manisoftwartist/perspectiveproj/blob/master/perspective.ipynb
# http://planning.cs.uiuc.edu/node102.html
class PerspectiveTransform(object):
    def __init__(self, x, y, z, scale, fovy):
        self.x = x
        self.y = y
        self.z = z
        self.scale = scale
        self.fovy = fovy

    def transform_image(self, src, gpu=False):
        if len(src.shape) > 2:
            H, W, C = src.shape
        else:
            H, W = src.shape

        M33, sl, _, ptsOut = self.get_warp_matrix(W, H, self.x, self.y, self.z, self.scale, self.fovy)
        sl = int(sl)

        dst = warpPerspective(src, M33, sl)

        return dst, M33, ptsOut

    def transform_pnts(self, pnts, M33):
        """
        :param pnts: 2D pnts, left-top, right-top, right-bottom, left-bottom
        :param M33: output from transform_image()
        :return: 2D pnts apply perspective transform
        """
        pnts = np.asarray(pnts, dtype=np.float32)
        pnts = np.array([pnts])
        dst_pnts = cv2.perspectiveTransform(pnts, M33)[0]

        return dst_pnts

    def get_warped_pnts(self, ptsIn, ptsOut, W, H, sidelength):
        ptsIn2D = ptsIn[0, :]
        ptsOut2D = ptsOut[0, :]
        ptsOut2Dlist = []
        ptsIn2Dlist = []

        for i in range(0, 4):
            ptsOut2Dlist.append([ptsOut2D[i, 0], ptsOut2D[i, 1]])
            ptsIn2Dlist.append([ptsIn2D[i, 0], ptsIn2D[i, 1]])

        pin = np.array(ptsIn2Dlist) + [W / 2., H / 2.]
        pout = (np.array(ptsOut2Dlist) + [1., 1.]) * (0.5 * sidelength)
        pin = pin.astype(np.float32)
        pout = pout.astype(np.float32)

        return pin, pout

    def get_warp_matrix(self, W, H, x, y, z, scale, fV):
        fVhalf = np.deg2rad(fV / 2.)
        d = np.sqrt(W * W + H * H)
        sideLength = scale * d / np.cos(fVhalf)
        h = d / (2.0 * np.sin(fVhalf))
        n = h - (d / 2.0)
        f = h + (d / 2.0)

        # Translation along Z-axis by -h
        T = np.eye(4, 4)
        T[2, 3] = -h

        # Rotation matrices around x,y,z
        R = get_rotate_matrix(x, y, z)

        # Projection Matrix
        P = np.eye(4, 4)
        P[0, 0] = 1.0 / np.tan(fVhalf)
        P[1, 1] = P[0, 0]
        P[2, 2] = -(f + n) / (f - n)
        P[2, 3] = -(2.0 * f * n) / (f - n)
        P[3, 2] = -1.0

        # pythonic matrix multiplication
        M44 = reduce(lambda x, y: np.matmul(x, y), [P, T, R])

        # shape should be 1,4,3 for ptsIn and ptsOut since perspectiveTransform() expects data in this way.
        # In C++, this can be achieved by Mat ptsIn(1,4,CV_64FC3);
        ptsIn = np.array([[
            [-W / 2., H / 2., 0.],
            [W / 2., H / 2., 0.],
            [W / 2., -H / 2., 0.],
            [-W / 2., -H / 2., 0.]
        ]])
        ptsOut = cv2.perspectiveTransform(ptsIn, M44)

        ptsInPt2f, ptsOutPt2f = self.get_warped_pnts(ptsIn, ptsOut, W, H, sideLength)

        # check float32 otherwise OpenCV throws an error
        assert (ptsInPt2f.dtype == np.float32)
        assert (ptsOutPt2f.dtype == np.float32)
        M33 = cv2.getPerspectiveTransform(ptsInPt2f, ptsOutPt2f).astype(np.float32)

        return M33, sideLength, ptsInPt2f, ptsOutPt2f