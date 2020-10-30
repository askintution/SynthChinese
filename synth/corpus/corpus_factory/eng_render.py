import random
from synth.corpus.corpus_factory.base_render import BaseRender


class EngRender(BaseRender):
    """
    生成英文字母串：
        - 12位英文字母
    """

    def get_sample(self):
        en_words = u'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        words = ''.join(random.choices(en_words, k=12))
        return words

    def generate(self, size):
        for _ in range(size):
            yield self.get_sample()

if __name__ == '__main__':
    r = EngRender('../data/chars/chn.txt')
    for _ in range(100):
        print(r.get_sample())