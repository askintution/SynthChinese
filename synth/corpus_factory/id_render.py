import random
from _datetime import datetime, timedelta
from synth.corpus_factory.base_render import BaseRender


class IDRender(BaseRender):
    """
    生成ID类words：
        - 身份证号（校验）
    """

    def get_check_digit(self, id_number):
        """ 通过身份证号获取校验码 """
        check_sum = 0
        for i in range(0, 17):
            check_sum += ((1 << (17 - i)) % 11) * int(id_number[i])
        check_digit = (12 - (check_sum % 11)) % 11
        return check_digit if check_digit < 10 else 'X'

    def get_sample(self):
        """ 随机生成身份证号，sex = 0表示女性，sex = 1表示男性 """

        # 随机生成一个区域码(6位数)
        id_number = str(random.randint(110000, 659001))
        # 限定出生日期范围(8位数)
        start, end = datetime.strptime("1960-01-01", "%Y-%m-%d"), datetime.strptime("2050-12-30", "%Y-%m-%d")
        birth_days = datetime.strftime(start + timedelta(random.randint(0, (end - start).days + 1)), "%Y%m%d")
        id_number += str(birth_days)
        # 顺序码(2位数)
        id_number += str(random.randint(10, 99))
        # 性别码(1位数)
        if random.random() < 0.5:
            sex = 0  # 女性
        else:
            sex = 1
        id_number += str(random.randrange(sex, 10, step=2))
        # 校验码(1位数)
        return id_number + str(self.get_check_digit(id_number))

    def generate(self, size):
        for _ in range(size):
            yield self.get_sample()


if __name__ == '__main__':
    r = IDRender('../data/chars/chn.txt')
    for _ in range(100):
        print(r.get_sample())
