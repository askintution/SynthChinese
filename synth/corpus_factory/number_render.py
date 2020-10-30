import random
from synth.corpus_factory.base_render import BaseRender


class NumberRender(BaseRender):
    """
    生成数字words：
        - (0, 1000)均匀分布, 50%随机带 kg/mm/㎡ 符号
        - 均值0，标准差1000,保留0、1、2、3、4位小数
    """
    def load(self):
        pass

    def get_sample(self):
        if random.random() < 0.5:
            num = random.randint(0, 1000)
            word = str(num)
            if random.random() < 0.5:
                unit = random.choices(['kg', 'mm', '㎡'], weights=[0.5, 0.3, 0.2])[0]
                word += unit
        else:
            num = random.gauss(0, 1000)
            digits = random.choices([0, 1, 2, 3, 4], weights=[0.4, 0.2, 0.2, 0.1, 0.1])[0]
            word = str(round(num, digits))
        return word

    def generate(self, size):
        for _ in range(size):
            yield self.get_sample()


if __name__ == '__main__':
    r = NumberRender('../data/chars/chn.txt')
    for _ in range(100):
        print(r.get_sample())