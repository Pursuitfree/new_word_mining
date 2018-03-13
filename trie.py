"""
The trie tree implementation.
Author: tangxuan
"""
import numpy as np


class VisualWord(object):
    """
    虚词类。
    所谓虚词，即corpus中的索引，存放索引能节约存储空间
    """
    corpus = None  # 虚词的真实语料库，所有虚词对象共用同一语料库

    def __init__(self, d=-1, start=-1, end=-1):
        """
        语料库实际上是由句子构成的元组
        :param d: 句子在corpus中的索引
        :param start: 真实词在句子中的开始索引
        :param end: 真实词在句子中的结束索引
        """
        self.d = d
        self.start = start
        self.end = end

        self.index = start  # 用作迭代
        self._reverse = False  # 用于标识当前虚词是否被逆置的标记

    @property
    def length(self):
        return self.end - self.start

    @property
    def sub_words(self):
        """
        返回当前词的最小可分割对象的序列，该序列的元素亦是虚词类对象
        :return: 词的最小可分割对象的序列
        """
        return [VisualWord(self.d, i, i + 1) for i in range(self.start, self.end)]

    def reverse(self, inplace=False):
        """
        将虚词逆置
        :param inplace: 决定是否原地逆置的参数
        :return: 由inplace参数决定返回值。
                 如果inplace为真，则当前虚词对象会被逆置并作为返回值被返回；
                 否则返回当前词逆置后的副本。
        """
        if inplace:
            self._reverse = not self._reverse
            return self

        res = VisualWord(self.d, self.start, self.end)
        res.reverse(inplace=True)
        return res

    def decode(self):
        """
        将虚词解码为真实词。
        :return: 当前虚词对应的真实词
        """
        d = self.d
        start = self.start
        end = self.end

        return self.corpus.slice(d, start, end)

    def partition(self):
        """
        将虚词分割为任意可能的左右子序列。
        :return: 任意可能左右子序列的列表。
        """
        _res = []
        d = self.d
        x = self.start
        y = self.end

        class Parts(object):
            pass

        for i in range(x + 1, y):
            parts = Parts()
            parts.left = VisualWord(d, x, i)
            parts.right = VisualWord(d, i, y)
            _res.append(parts)
        return _res

    def __hash__(self):
        return self.decode().__hash__()

    def __eq__(self, other):
        return (self.corpus.slice(self.d, self.start, self.end)
                == self.corpus.slice(other.d, other.start, other.end))

    def __len__(self):
        return self.length

    def __getitem__(self, key):
        if isinstance(key, int):
            if self._reverse:
                key = self.length - key - 1
            return VisualWord(self.d, self.start + key, self.start + key + 1)
        else:
            raise ValueError()

    def __iter__(self):
        if self._reverse:
            self.index = self.end
        return self

    def next(self):
        if self._reverse:
            if self.index <= self.start:
                raise StopIteration()
            else:
                res = VisualWord(self.d, self.index - 1, self.index)
                self.index -= 1
                return res
        else:
            if self.index >= self.end - 1:
                raise StopIteration()
            else:
                res = VisualWord(self.d, self.index, self.index + 1)
                self.index += 1
                return res


class Node(object):
    """
    trie树的结点类，存储该结点的相关信息。
    """

    def __init__(self, vword):
        """
        结点的构造函数
        :param vword: 结点对应的值，该值为虚词对象
        """
        self.value = vword
        self.count = 0  # 结点所代表的词的频次
        self.children = dict()  # 结点的所有子结点

    def update(self):
        self.count += 1

    def add_child(self, new_child):
        self.children[new_child.value] = new_child

    @property
    def decode(self):
        return self.value.decode()

    def __eq__(self, other):
        return self.value == other.key

    def __len__(self):
        return len(self.value)


class Trie(object):
    """
    trie树类，用以查询特定词在语料库中的出现频次以及其他相关信息
    """
    reverse = False  # 用以标识是否倒序插入词的标记

    def __init__(self, reverse=False):
        self.root = Node('$')
        self.reverse = reverse

    def build(self, data):
        for vword in data:
            if self.reverse:
                vword = vword.reverse()
            self.insert(vword)

    def insert(self, vword):
        index, node = self.find_last_node(vword)
        while index < len(vword):
            item = vword[index]
            new_node = Node(item)
            node.add_child(new_node)
            node = new_node
            index += 1
        node.update()

    def search(self, vword):
        index, node = self.find_last_node(vword)
        if index == len(vword):
            return node.count
        else:
            return 0

    def prefix_search(self, prefix):
        if self.reverse:
            prefix = prefix.reverse()
        index, node = self.find_last_node(prefix)
        if index != len(prefix):
            raise ValueError("No such data '" + prefix.decode() + "' in the trie.")
        else:
            cnts = [v.count for v in node.children.values()]

            return np.array(cnts)

    def find_last_node(self, vword):
        node = self.root
        index = 0
        while index < len(vword):
            item = vword[index]
            if item in node.children:
                index += 1
                node = node.children[item]
            else:
                break
        return index, node


if __name__ == '__main__':
    pass
