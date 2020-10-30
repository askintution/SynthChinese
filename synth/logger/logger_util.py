# -*- coding:utf-8 -*-
"""
@author zhangjian

main func
--------
get_rotating_logger:
返回一个logger实例，当mail_level不为空时, 包含三个handler[file_handler、console_handler、mail_handler]
分别用来将日志写入文件、打印到consolse、发送到邮箱

logger方法说明：
------
DEBUG: logger.debug: 调试信息，可记录详细的业务处理到哪一步了，以及当前的变量状态
INFO: logger.info: 有意义的事件信息，如程序启动，关闭事件，收到请求事件等；
WARNING: logger.warning: 警告信息, 运行状态不是期望的但仍可继续处理等；
ERROR: logger.error: 错误信息。[建议]在except中用logger.exception: 输出错误信息并捕捉异常原因
CRITICAL: logger.critical: 严重错误
"""

import re
import logging
import time
import signal
import sys
from functools import wraps
from logging.handlers import TimedRotatingFileHandler

PATERN = '[%(asctime)s-%(name)s-%(levelname)s]-%(filename)s-%(funcName)s-%(lineno)s-%(message)s'


class Logger(logging.Logger):
    CRITICAL = 50
    FATAL = CRITICAL
    ERROR = 40
    WARNING = 30
    WARN = WARNING
    INFO = 20
    DEBUG = 10
    NOTSET = 0

    def __init__(self, name, dir, prefix, when='D', interval=7, backupCount=10, console=False, level=DEBUG,
                 mail_level=None, mailhost=None, fromaddr=None, toaddrs=None, subject=None, credentials=None):
        """
        name: logger名称
        dir: 日志文件存放路径
        prefix: 日志文件前缀。（日志文件名称为prefix-2018-07-10.log形式）
        when: 描述滚动周期的基本单位
        interval: 滚动周期
        backupCount: 日志文件的保留个数

        console: Boolean, 是否添加stream handler

        mail_level: 发送警报邮件的日级别：如logging.ERROR即40
        mailhost: tuple, (host, port)
        fromaddr: 发件人
        toaddrs: 收件人
        subject: 主题
        credentials: tuple, (usr_name, usr_pwd)

        """
        super(Logger, self).__init__(name)
        self.setLevel(level)  # 设置日志级别

        formatter = logging.Formatter(PATERN)

        # ------file handler------
        filename = dir + "/" + prefix  # 日志文件名称
        # 日志保留90天,一天保存一个文件
        file_handler = TimedRotatingFileHandler(filename, when=when, interval=interval, backupCount=backupCount)

        # 删除设置
        file_handler.suffix = '%Y-%m-%d_%H-%M.log'  # 日志文件后缀
        file_handler.extMatch = re.compile(r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}.log$")  # 删除匹配
        # 定义日志文件中格式
        file_handler.setFormatter(formatter)  # 可以通过setFormatter指定输出格式
        self.addHandler(file_handler)
        # ------console handler------
        if console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.formatter = formatter  # 也可以直接给formatter赋值
            self.addHandler(console_handler)
        # ------mail handler------
        if mail_level:
            mail_handler = logging.handlers.SMTPHandler(mailhost, fromaddr, toaddrs, subject, credentials)
            mail_handler.formatter = formatter  # 也可以直接给formatter赋值
            mail_handler.setLevel(mail_level)
            self.addHandler(mail_handler)

        self.addHandler(file_handler)

    def add_surfix(self, surfix):
        formatter = logging.Formatter(PATERN+surfix)
        for handler in self.handlers:
            handler.setFormatter(formatter)

    def remove_surfix(self):
        formatter = logging.Formatter(PATERN)
        for handler in self.handlers:
            handler.setFormatter(formatter)

    def func_runtime(self, func):
        """
        耗时修饰器：计算函数耗时并写入日志的
        """
        @wraps(func)
        def deco(*args, **kwargs):
            start = time.time()
            res = func(*args, **kwargs)
            end = time.time()
            delta = end - start
            self.info(func.__name__ + ' run time[ms]:' + str(delta * 1000))
            return res
        return deco

    def log_time_delta(self, info=""):
        # 计算上次运行本函数至本次运行的时间
        if not self._last_time:
            self._last_time = time.time()
        else:
            delta = time.time()-self._last_time
            self.info(info + '\t time delta: ' + str(delta * 1000))

    def func_runtime_limit(self, num, callback):
        def wrap(func):
            def handle(signum, frame):  # 收到信号 SIGALRM 后的回调函数，第一个参数是信号的数字，第二个参数是the interrupted stack frame.
                raise RuntimeError

            @wraps(func)
            def to_do(*args, **kwargs):
                try:
                    signal.signal(signal.SIGALRM, handle)  # 设置信号和回调函数
                    signal.alarm(num)  # 设置 num 秒的闹钟
                    r = func(*args, **kwargs)
                    signal.alarm(0)  # 关闭闹钟
                    return r
                except RuntimeError as e:
                    callback()  # do sth after timeout

            return to_do

        return wrap

