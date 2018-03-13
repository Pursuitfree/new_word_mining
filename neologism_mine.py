"""
Chinese neologism mining algorithm.
Author: tangxuan
"""

import numpy as np
from trie import Trie, VisualWord
from probability import compute_pmi
from probability import entropy
from text_process import process
from text_process import seg_with_custom_dict


class WordInfo(object):
    total = 0

    def __init__(self):
        self.vword = None
        self.real_word = None
        self.count = 0
        self.score = 0.0

    def __eq__(self, other):
        return self.real_word == other.real_word

    def __hash__(self):
        return self.real_word.__hash__()


class Mine(object):
    def __init__(self, doc, n_gram=5, min_len=2, custom_dict_path=None):
        sentences = process(doc)

        self.corpus = seg_with_custom_dict(sentences, custom_dict_path)
        VisualWord.corpus = self.corpus
        self.n_gram = n_gram
        self.min_len = min_len

        candidates = self.gen_candidates(self.corpus)

        self.total = len(candidates)
        WordInfo.total = self.total

        self.prefix_trie = Trie()
        self.suffix_trie = Trie(reverse=True)

        self.prefix_trie.build(candidates)
        self.suffix_trie.build(candidates)

        self.words_info = list(set([self.calculate(candidate) for candidate in candidates
                                    if self.min_len <= len(candidate) <= self.n_gram]))

        avg = np.array([w.score * w.count for w in self.words_info]).mean()
        self.words_info = [w for w in self.words_info if w.score * w.count > avg]
        self.filter_sub_words()
        self.words_info.sort(key=lambda w: w.score * w.count, reverse=True)
        self.real_words = [wi.real_word for wi in self.words_info]

    def filter_sub_words(self):
        vwords = [wi.vword for wi in self.words_info]
        pre_trie = Trie()
        suf_trie = Trie(reverse=True)
        pre_trie.build(vwords)
        suf_trie.build(vwords)
        words_info = set()
        for wi in self.words_info:
            vword = wi.vword
            left = self.get_word_count(vword, prefix_search=True, suffix=True)
            right = self.get_word_count(vword, prefix_search=True, suffix=False)
            is_suf = len(left) > 0
            is_pre = len(right) > 0
            if not is_suf and not is_pre:
                words_info.add(wi)
                pre = ('住所地', '住所', '住')
                suf = ('分行', '公司')

                for p in pre:
                    if wi.real_word.startswith(p):
                        wi.real_word = wi.real_word.replace(p, '')
                        break
                for s in suf:
                    idx = wi.real_word.find(s)
                    if idx != -1:
                        idx += len(s)
                        wi.real_word = wi.real_word[0:idx]
                        break

        self.words_info = list(words_info)

    def calculate(self, vword):
        res = WordInfo()
        res.vword = vword
        res.real_word = vword.decode()
        res.count = self.get_word_count(vword)

        # print(res.real_word, res.count)

        sub_parts = vword.partition()
        l_counts = np.array([self.get_word_count(sub.left) for sub in sub_parts])
        r_counts = np.array([self.get_word_count(sub.right) for sub in sub_parts])
        res.aggregation = compute_pmi(self.total, res.count, l_counts, r_counts)

        left = self.get_word_count(vword, prefix_search=True, suffix=True)
        right = self.get_word_count(vword, prefix_search=True, suffix=False)

        res.left = left
        res.right = right

        res.left_entropy = entropy(left)
        res.right_entropy = entropy(right)

        res.entropy = min(res.left_entropy, res.right_entropy)
        res.score = res.aggregation + res.entropy
        return res

    def get_word_count(self, vword, prefix_search=False, suffix=False):
        if suffix:
            if prefix_search:
                res = self.suffix_trie.prefix_search(vword)
            else:
                res = self.suffix_trie.search(vword)
        else:
            if prefix_search:
                res = self.prefix_trie.prefix_search(vword)
            else:
                res = self.prefix_trie.search(vword)
        return res

    def gen_candidates(self, corpus):
        candidates = list()
        n_gram = self.n_gram + 1  # 为了计算左右信息熵
        d = 0
        for sentence in corpus.data:
            n = len(sentence)
            if n < 2:
                d += 1
                continue
            for i in range(n):
                for j in range(i + 1, min(i + n_gram + 1, n + 1)):
                    candidate = VisualWord(d=d, start=i, end=j)
                    candidates.append(candidate)
            d += 1

        return candidates


if __name__ == '__main__':
    import os

    main_dir = r"D:\programData\20171025_38293\北京"
    for d1 in os.listdir(main_dir):
        f1 = os.path.join(main_dir, d1)
        first = os.listdir(f1)
        for d2 in first:
            f2 = os.path.join(f1, d2)
            second = os.listdir(f2)
            for f3 in second:
                fname = os.path.join(f2, f3)
                if f3.startswith('newWords_'):
                    os.remove(fname)
                    continue
                with open(fname) as f:
                    doc = f.read()
                    mine = Mine(doc, n_gram=20, min_len=2)
                    new_words = mine.real_words
                    print(new_words)

                    out_f = os.path.join(f2, 'newWords_' + f3)
                    with open(out_f, 'w', encoding='utf-8') as o:
                        o.write('\n'.join(new_words))
                        # file_name = os.path.join(file_dir, file_name)

                        # _in = open(file_name)
                        # doc = _in.read()
                        #
                        # import time
                        #
                        # start = time.time()
                        # mine = Mine(doc, n_gram=4)
                        # stop = time.time()
                        # print('time expense: ', stop - start, 's.')
                        # print(' '.join(mine.real_words))
