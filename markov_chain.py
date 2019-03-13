import MeCab
import csv
import random
import sys

mecab = MeCab.Tagger("-Owakati")
BOS = '[BOS]'
EOS = '[EOS]'

def parse(s):
    """形態素解析（分かち書き）"""
    return mecab.parse(s).strip().split(' ')

def train(ctx_len, dataset):
    tp = {}  # transition probability
    for sen in dataset:
        words = [BOS] + sen + [EOS]
        ctx = tuple([None for i in range(ctx_len)])
        # 単語のペアの回数を数える
        for w in words:
            if ctx not in tp:
                tp[ctx] = {}
            if w not in tp:
                tp[ctx][w] = 0

            tp[ctx][w] += 1
            ctx = tuple(list(ctx)[1:] + [w])

    # 出現確率に変換
    for ctx in tp.keys():
        n = 0
        for w in tp[ctx].keys():
            n += tp[ctx][w]
        for w in tp[ctx].keys():
            tp[ctx][w] /= n
    return tp

def choose_next_word(tp, ctx):
    x = random.random()
    p = 0.0
    for w in tp[ctx].keys():
        p += tp[ctx][w]
        if p > x:
            return w
    return w

def generate(ctx_len, tp):
    sen = []
    ctx = tuple([None for i in range(ctx_len-1)] + [BOS])
    while True:
        w = choose_next_word(tp, ctx)
        if w == EOS:
            break
        sen.append(w)
        ctx = tuple(list(ctx)[1:] + [w])
    return sen

if __name__ == '__main__':
    dataset = []
    for fpath in sys.argv[1:]:
        with open(fpath, 'r') as fin:
            for row in csv.DictReader(fin):
                s = row['poem'].split('\\n')[0]
                dataset.append(s)

    ctx_len = 2
    tp = train(ctx_len, [parse(s) for s in dataset])
    while True:
        sen = ''.join(generate(ctx_len, tp))
        if sen not in dataset:
            print(sen)
            break
