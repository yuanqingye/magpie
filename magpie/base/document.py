from __future__ import print_function, unicode_literals

import re
import io
import os
import nltk
import string
import jieba

from nltk.tokenize import WordPunctTokenizer, sent_tokenize, word_tokenize

nltk.download('punkt', quiet=True)  # make sure it's downloaded before using

class Document(object):

    """ Class representing a document that the keywords are extracted from """
    def __init__(self, doc_id, filepath, text=None):
        self.doc_id = doc_id

        if text:
            text = self.clean_text(text)
            text = self.seg_text(text)
            self.text = text
            self.filename = None
            self.filepath = None
        else:  # is a path to a file
            if not os.path.exists(filepath):
                raise ValueError("The file " + filepath + " doesn't exist")

            self.filepath = filepath
            self.filename = os.path.basename(filepath)
            with io.open(filepath, 'r', encoding='gbk') as f:
                text_context = f.read()
                text_context = self.clean_text(text_context)
                self.text = self.seg_text(text_context)
                print(self.text)
        self.wordset = self.compute_wordset()



    # 利用jieba包进行分词，并并且去掉停词，返回分词后的文本
    def seg_text(self,text):
        stop = [line.strip() for line in open('data/stopwords.txt', encoding='utf8').readlines()]
        text_seged = jieba.cut(text.strip())
        outstr = ''
        for word in text_seged:
            if word not in stop:
                outstr += word
                outstr += ""
        return outstr.strip()

    # 清洗文本，去除标点符号数字以及特殊符号
    def clean_text(self,content):
        text = re.sub(r'[+——！，；／·。？、~@#￥%……&*“”《》：（）［］【】〔〕]+', '', content)
        text = re.sub(r'[▲!"#$%&\'()*+,-./:;<=>\\?@[\\]^_`{|}~]+', '', text)
        text = re.sub('\d+', '', text)
        text = re.sub('\s+', '', text)
        return text

    def __str__(self):
        return self.text

    def compute_wordset(self):
        tokens = WordPunctTokenizer().tokenize(self.text)
        lowercase = [t.lower() for t in tokens]
        return set(lowercase) - {',', '.', '!', ';', ':', '-', '', None}

    def get_all_words(self):
        """ Return all words tokenized, in lowercase and without punctuation """
        return [w.lower() for w in word_tokenize(self.text)
                if w not in string.punctuation]

    def read_sentences(self):
        lines = self.text.split('\n')
        raw = [sentence for inner_list in lines
               for sentence in sent_tokenize(inner_list)]
        return [[w.lower() for w in word_tokenize(s) if w not in string.punctuation]
                for s in raw]
