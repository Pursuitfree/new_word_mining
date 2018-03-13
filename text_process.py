import re


class Corpus(object):
    def __init__(self, data):
        self.data = data

    @property
    def size(self):
        _size = 0
        if len(self.data) > 0:
            for _ in self.data:
                _size += len(_)
        return _size

    def item(self, d, i):
        return self.data[d][i]

    def slice(self, d, x, y):
        return self.data[d][x:y]


def process(raw_doc):
    reg = '[ <>/?:;\'\"[\\]{}()\\|~!@#$%^&*\\-_=+《》“”‘’｛｝【】（）…￥]+'
    pat = re.compile(reg)
    raw_doc = re.sub(pat, '', raw_doc)

    reg = '[\\s,.<>/?，。《》、？：；！—┄－]+'
    pat = re.compile(reg)
    sentences = re.split(pat, raw_doc)
    if len(sentences) > 0:
        if len(sentences[0]) < 1:
            sentences.remove(sentences[0])
        if len(sentences[-1]) < 1:
            sentences.remove(sentences[-1])
    sentences = tuple(sentences)

    return sentences


def seg_with_custom_dict(sentences, custom_dict_path=None):
    if custom_dict_path:
        return []
    else:
        corpus = Corpus(sentences)
        return corpus
