import random
from synth.corpus.corpus_factory.base_render import BaseRender


class TaskRender(BaseRender):
    """
    根据营业执照、车辆合格证、发票、房本识别任务增加任务相关语料
    """
    def __init__(self):
        self.load('data/corpus/yyzz-hgz-hc.txt')

    def load(self, file_path):
        lines = open(file_path, encoding='utf-8').readlines()
        self.lines = lines

    def get_sample(self):
        pass

    def generate(self, size):
        num = 0
        while True:
            for line in self.lines:
                yield line.strip()
                num += 1
                if num > size:
                    return


if __name__ == '__main__':
    r = TaskRender()
    words = r.generate(100)