# -*- coding:utf-8 -*-
"""
@author zhangjian
"""
from collections import OrderedDict
from synth.corpus.corpus_factory.base_render import BaseRender
from synth.corpus.corpus_factory.date_render import DateRender
from synth.corpus.corpus_factory.eng_render import EngRender
from synth.corpus.corpus_factory.id_render import IDRender
from synth.corpus.corpus_factory.number_render import NumberRender
from synth.corpus.corpus_factory.subaddr_render import SubAddrRender


def get_corpus(cfg):
    cfg = cfg['TEXT']
    sample_size = cfg['SAMPLE']['SAMPLE_SIZE']
    # corpus
    corpus_render = BaseRender(cfg['SAMPLE']['CHAR_SET'],
                               corpus_dir=cfg['CORPUS']['CORPUS_DIR'],
                               corpus_type_dict=cfg['CORPUS']['CORPUS_TYPE'],
                               corpus_weight_dict=cfg['CORPUS']['CORPUS_WEIGHT'],
                               char_max_amount=cfg['SAMPLE']['CHAR_MAX_AMOUNT'],
                               char_min_amount=cfg['SAMPLE']['CHAR_MIN_AMOUNT'],
                               length=cfg['SAMPLE']['WORD_LENGTH'],
                               )
    date_render = DateRender(cfg['SAMPLE']['CHAR_SET'])
    number_render = NumberRender(cfg['SAMPLE']['CHAR_SET'])
    eng_render = EngRender(cfg['SAMPLE']['CHAR_SET'])
    id_render = IDRender(cfg['SAMPLE']['CHAR_SET'])
    sub_addr_render = SubAddrRender(cfg['SAMPLE']['CHAR_SET'])

    all_renders = OrderedDict()
    all_renders['corpus'] = corpus_render
    all_renders['date'] = date_render
    all_renders['number'] = number_render
    all_renders['sub_address'] = sub_addr_render
    all_renders['id'] = id_render
    all_renders['eng_char'] = eng_render

    all_generators = OrderedDict()
    for render_name in all_renders:
        amount = sample_size[render_name] * 10000
        all_generators[render_name] = all_renders[render_name].generate(amount)
    return all_generators

