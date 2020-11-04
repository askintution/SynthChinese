# -*- coding:utf-8 -*-
"""
@author zhangjian

"""
import os
from synth.logger.logger_util import Logger


log_path = os.path.dirname(os.path.abspath(__file__)) + "../../../log"

args = {'when': 'D',
        'interval': 1,
        'backupCount': 10,
        'console': True,  # 是否输出到屏幕
        'level': Logger.INFO,  # 日志level
        }

logger = Logger('synth', log_path, 'synth_chinese', **args)
