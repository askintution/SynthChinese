import random
import glob
import os
from abc import abstractmethod


class BaseRender(object):
    """
    根据语料文件产生words：
        -可指定多个语料文件，每次以指定的corpus_weight_dict随机选取一个语料文件并产生words
        -可设定单个字符出现的频率，如超过该频率，则停用该字符
        -单一语料用完后不再生成该语料的words，全部语料用完后如mode为infinite则重新进行加载，否则停止产生新words
        -生成完毕后，可根据词频补充不常出现的字符

    """

    def __init__(self, chars_file,
                 corpus_dir=None,
                 corpus_type_dict=None,
                 corpus_weight_dict=None,
                 char_max_amount=None,
                 char_min_amount=200,
                 length=None,

                 mode="infinite"):
        """
        :param chars: List of charset
        :param corpus_dir: Path of corpus
        :param corpus_type_dict: {corpus_short_name1: corpus_type...}, copus type "article"、"list"
        :param corpus_weight_dict: Weight of corpus {corpus_short_name1: weith1, ...}
        :param char_max_amount: Max amount of single char
        :param length: [min_length, max_length], lenght range of word length
        :param mode: if "infinite" reload corpus when all corpus are end, else raise error
        """
        self.chars = self.load_chars(chars_file)
        self.stastics = dict()
        for c in self.chars:
            self.stastics[c] = 0

        self.corpus_dir = corpus_dir

        if char_max_amount:
            self.char_max_amount = char_max_amount
        else:
            self.char_max_amount = float('inf')

        self.char_min_amount = char_min_amount
        if isinstance(length, list):
            self.length = length
        else:
            self.length = [1, 12]

        self.corpus_type = corpus_type_dict
        self.corpus_weight = corpus_weight_dict
        self.mode = mode
        self.load()

    def load_chars(self, filepath):
        """
        Load charset file
        """
        if not os.path.exists(filepath):
            print("Chars file not exists.")
            exit(1)

        ret = ' '
        with open(filepath, 'r', encoding='utf-8') as f:
            while True:
                line = f.readline()
                if not line:
                    break
                ret += line[0]
        return ret

    def load_corpus_path(self):
        """
        load paths of corpus
        """
        print(f"Loading corpus from: {self.corpus_dir}")
        self.corpus_path = glob.glob(self.corpus_dir + '/**/*.txt', recursive=True)
        if len(self.corpus_path) == 0:
            print("Corpus not found.")
            exit(-1)

    def gen_words_from_corpus(self, corpus_file_name, corpus_type):
        """
        generator for single corpus_file, yield one word of specified length each time
        """
        with open(corpus_file_name, mode='r') as f:
            cache = f.readline().strip()
            while True:
                nchar = random.randint(self.length[0], self.length[1])
                words = ""
                while True:
                    if cache:
                        char = cache[0]
                        cache = cache[1:]
                        if (char in self.chars) and (self.stastics[char] < self.char_max_amount):
                            words += char
                            self.stastics[char] += 1
                        if len(words) == nchar:
                            yield words
                            break  # genrate next word

                    else:
                        line = f.readline()
                        if line:
                            if corpus_type == 'list':
                                cache += ' '  # add space-char when add next line
                            cache += line
                        else:
                            return -1  # corps end

    def load(self):
        """
        load all corpus as a generator dict, use default weigth if it's not specified
        """
        if self.corpus_dir:
            self.load_corpus_path()
            self.corpus = {}
            print(f'Weight of corpus:{self.corpus_weight}')
            for corpus_file_name in self.corpus_path:
                corpus_short_name = os.path.split(corpus_file_name)[1]

                if isinstance(self.corpus_type, dict):
                    if corpus_short_name in self.corpus_type:
                        corpus_type = self.corpus_type[corpus_short_name]
                    else:
                        # use 'article' if not specified
                        corpus_type = 'article'
                else:
                    corpus_type = 'article'

                if isinstance(self.corpus_weight, dict):
                    if corpus_short_name in self.corpus_weight:
                        weight = self.corpus_weight[corpus_short_name]
                        generator = self.gen_words_from_corpus(corpus_file_name, corpus_type)
                        self.corpus[corpus_short_name] = {'corpus': generator,
                                                          'weight': weight}
                        print(f'Weight of corpus:{corpus_short_name}: {weight}')
                    else:
                        print(f'Weight of corpus:{corpus_short_name}, not setted! use 0')

                else:
                    weight = 0.01
                    print(f'Weight of corpus:{corpus_short_name}, not setted! use 0.01')
                    self.corpus[corpus_short_name] = {'corpus': self.gen_words_from_corpus(corpus_file_name, corpus_type),
                                                      'weight': weight}
        else:
            pass

    @abstractmethod
    def get_sample(self):
        """
        generate one sample
        """
        if not self.corpus:
            # all corpus exhausted
            if self.mode == 'infinite':
                # reload
                self.load()
            else:
                raise StopIteration
        weights = []
        for val in self.corpus.values():
            weight = val['weight']
            weights.append(weight)
        corpus_short_name = random.choices(list(self.corpus), weights=weights)[0]
        try:
            word = next(self.corpus[corpus_short_name]['corpus'])
        except StopIteration:
            self.corpus.pop(corpus_short_name)
            print(f'{corpus_short_name}: is exhausted！')
            return self.get_sample()
        return word

    def generate(self, size):
        for _ in range(size):
            yield self.get_sample()
        for text in self.supply_uncommon():
            yield text

    def supply_uncommon(self):
        """
        supply uncommon words
        """
        words = []
        parag = []
        for c in self.chars:
            c_amount = self.stastics[c]
            if c_amount < self.char_min_amount:
                added_amount = self.char_min_amount - c_amount
                tmp_list = [c]
                parag.extend(tmp_list * added_amount)
                self.stastics[c] = self.char_min_amount

        random.shuffle(parag)
        parag = ''.join(parag)
        index = 0
        words_count = int(len(parag) / self.length[1])
        while (index < words_count):
            word = parag[self.length[1] * index: self.length[1] * (index + 1)]
            words.append(word)
            index += 1

        return words

    def supply_difficult(self, difficult_file, amount=100000):
        """
        supply difficult
        """
        ds_words = []
        while True:
            lines = open(difficult_file, encoding='utf-8').readlines()
            for line in lines:
                words = random.choices(line.strip(), k=self.length[1])
                ds_words.append(''.join(words))
                if len(ds_words) >= amount:
                    return ds_words

    def supply_difficult_v2(self, difficult_file, times=6):
        """
        :param difficult_file:
        :return:
        """
        ds_words = []

        lines = open(difficult_file, encoding='utf-8').readlines()
        for line in lines:
            # true_times = 该行字数 * 行重复次数
            true_times = times * len(line.strip())
            for _ in range(true_times):
                words = random.choices(line.strip(), k=self.length[1])
                ds_words.append(''.join(words))
        return ds_words


if __name__ == '__main__':
    render = BaseRender('../../data/chars/chn.txt', '../../data/corpus', length=[12, 12])
    for _ in range(1000):
        print(render.get_sample())

    books = render.gen_words_from_corpus('../data/corpus/books.txt', 'list')
