import random
import glob
import os
from abc import abstractmethod
from synth.logger.synth_logger import logger


class BaseRender(object):
    """
    根据语料文件产生words：
        -可指定多个语料文件，每次以指定的corpus_weight_dict随机选取一个语料文件并产生words
        -可设定单个字符出现的频率，如超过该频率，则停用该字符
        -单一语料用完后不再生成该语料的words，全部语料用完后如mode为infinite则重新进行加载，否则停止产生新words
        -生成完毕后，可根据词频补充不常出现的字符

    """

    def __init__(self, chars_file, cfg=None):
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

        if cfg:
            self.char_max_amount = cfg['SAMPLE']['CHAR_MAX_AMOUNT']
            self.char_max_sub_str = cfg['SAMPLE']['CHAR_MAX_SUBSTR']
            self.char_min_amount = cfg['SAMPLE']['CHAR_MIN_AMOUNT']
            self.length = cfg['SAMPLE']['WORD_LENGTH']
            self.insert_blank = cfg['SAMPLE']['INSERT_BLANK_PROB']

            self.corpus_dir = cfg['CORPUS']['CORPUS_DIR']
            self.corpus_type = cfg['CORPUS']['CORPUS_TYPE']
            self.corpus_weight = cfg['CORPUS']['CORPUS_WEIGHT']
            self.infinite = cfg['CORPUS']['INFINITE']

            self.load()

    def load_chars(self, filepath):
        """
        Load charset file
        """
        if not os.path.exists(filepath):
            logger.error("Chars file not exists.")
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
        logger.info(f"Loading corpus from: {self.corpus_dir}")
        self.corpus_path = glob.glob(self.corpus_dir + '/**/*.txt', recursive=True)
        if len(self.corpus_path) == 0:
            logger.error("Corpus not found.")
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
                        if char in self.chars:
                            if self.stastics[char] < self.char_max_amount:
                                words += char
                                self.stastics[char] += 1
                            else:
                                words += self.char_max_sub_str
                        if len(words) == nchar:
                            # randomly insert blank
                            if nchar < self.length[1]:
                                if random.random() < self.insert_blank:
                                    words = self.randomly_insert_blank(words)
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
            # logger.info(f'Weight of corpus:{self.corpus_weight}')
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
                        logger.info(f'Weight of corpus:{corpus_short_name}: {weight}')
                    else:
                        logger.info(f'Weight of corpus:{corpus_short_name}, not setted! use 0')

                else:
                    weight = 0.01
                    logger.info(f'Weight of corpus:{corpus_short_name}, not setted! use 0.01')
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
            if self.infinite:
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
            logger.info(f'{corpus_short_name}: is exhausted！')
            return self.get_sample()
        return word

    @abstractmethod
    def generate(self, size):
        for _ in range(size):
            yield self.get_sample()
        for text in self.supply_uncommon():
            yield text

    def randomly_insert_blank(self, word):
        length_of_word = len(word)
        insert_blank_num = self.length[1]-length_of_word
        list_word = list(word)
        for _ in range(insert_blank_num):
            position = random.choice(range(1, len(list_word)))
            list_word.insert(position, ' ')
        return ''.join(list_word)


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
