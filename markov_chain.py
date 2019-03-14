import MeCab
import csv
import random
import sys
from argparse import ArgumentParser

neologd = '/usr/local/lib/mecab/dic/mecab-ipadic-neologd'
mecab = MeCab.Tagger("-Owakati -d " + neologd)
BOS = '[BOS]'
EOS = '[EOS]'

def parse(s):
    """形態素解析（分かち書き）"""
    return mecab.parse(s).strip().split(' ')

def normalize(table):
    """出現確率の総和が 1.0 になるように遷移行列を正規化する"""
    for ctx in table.keys():
        n = 0
        for w in table[ctx].keys(): n += table[ctx][w]
        for w in table[ctx].keys(): table[ctx][w] /= n

def train(ctx_len, dataset):
    table = {}  # transition probability
    for sen in dataset:
        words = [BOS] + sen + [EOS]
        ctx = tuple([None for i in range(ctx_len)])
        # 単語のペアの回数を数える
        for w in words:
            if ctx not in table: table[ctx] = {}
            if w not in table: table[ctx][w] = 0
            table[ctx][w] += 1
            ctx = tuple(list(ctx)[1:] + [w])

    normalize(table)
    return table

def choose_next_word(table, ctx):
    x = random.random()
    p = 0.0
    for w in table[ctx].keys():
        p += table[ctx][w]
        if p > x: return w
    return w

def generate(ctx_len, table):
    sen = []
    ctx = tuple([None for i in range(ctx_len-1)] + [BOS])
    while True:
        w = choose_next_word(table, ctx)
        if w == EOS: break
        sen.append(w)
        ctx = tuple(list(ctx)[1:] + [w])
    return sen

if __name__ == '__main__':
    parser = ArgumentParser(description='Lens poem generation by Markov chain')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='CSV file (training data)')
    parser.add_argument('--context', metavar='N', type=int, help='context length of Markov chain')
    args = parser.parse_args()

    dataset = []
    for fpath in args.files:
        with open(fpath, 'r') as fin:
            for row in csv.DictReader(fin):
                for s in row['poem'].split('\\n'):
                    dataset.append(s)

    ctx_len = args.context
    table = train(ctx_len, [parse(s) for s in dataset])
    while True:
        sen = ''.join(generate(ctx_len, table))
        if sen not in dataset:
            print(sen)
            break
