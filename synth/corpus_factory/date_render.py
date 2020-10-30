import random
import time
from synth.corpus_factory.base_render import BaseRender


class DateRender(BaseRender):
    """
    生成日期words：
        - %Y年%m月%d [%H:%M:%S]随机
        - %Y-%m-%d [%H:%M:%S]
        - %Y/%m/%d [%H:%M:%S]

    """

    def __init__(self, *args, **kwargs):
        super(DateRender, self).__init__(*args, **kwargs)
        self._init_date()

    def _init_date(self):
        a1 = (1976, 1, 1, 0, 0, 0, 0, 0, 0)  # 设置开始日期时间元组（1976-01-01 00：00：00）
        a2 = (2099, 12, 31, 23, 59, 59, 0, 0, 0)  # 设置结束日期时间元组（1990-12-31 23：59：59）

        self.start = time.mktime(a1)  # 生成开始时间戳
        self.end = time.mktime(a2)  # 生成结束时间戳
        self.formats = ['%Y年%m月%d', '%Y-%m-%d', '%Y/%m/%d']
        self.format_weights = [0.5, 0.3, 0.2]

    def get_sample(self):
        t = random.randint(self.start, self.end)  # 在开始和结束时间戳中随机取出一个
        date_touple = time.localtime(t)  # 将时间戳生成时间元组

        format = random.choices(self.formats, self.format_weights)[0]
        if random.random() < 0.3:
            format += ' %H:%M:%S'
        date = time.strftime(format, date_touple)  # 将时间元组转成格式化字符串（1976-05-21）
        return date

    def generate(self, size):
        for _ in range(size):
            yield self.get_sample()


if __name__ == '__main__':
    r = DateRender('../data/chars/chn.txt')
    for _ in range(100):
        print(r.get_sample())