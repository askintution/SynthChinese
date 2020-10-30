# -*- coding:utf-8 -*-
"""
@author zhangjian

"""

from synth.logger.logger_util import Logger

args = {'when': 'D',
        'interval': 1,
        'backupCount': 10,
        'console': True,  # 是否输出到屏幕
        'level': Logger.INFO,  # 日志level
        }

logger = Logger('synth', 'log', 'synth_chinese', **args)
