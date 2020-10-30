import random
from synth.corpus.corpus_factory.base_render import BaseRender


class SubAddrRender(BaseRender):
    """
    生成子地址：
        - **号院**号楼*单元
        - **区**弄**室
    """

    def get_sample(self):
        num_words = u'0123456789'
        num_chn = u'一二三四五六七八九'
        if random.random() < 0.8:
            word = f'{"".join(random.sample(num_words, 2))}号院{"".join(random.sample(num_words, 2))}号楼{"".join(random.sample(num_words+num_chn, 1))}单元'
        else:
            word = f'{"".join(random.sample(num_words, 2))}区{"".join(random.sample(num_words, 2))}弄{"".join(random.sample(num_words+num_chn, 1))}室'
        return word

    def generate(self, size):
        for _ in range(size):
            yield self.get_sample()


if __name__ == '__main__':
    r = SubAddrRender('../data/chars/chn.txt')
    for _ in range(100):
        print(r.get_sample())