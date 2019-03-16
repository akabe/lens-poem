from argparse import ArgumentParser
from keras.layers import Dense , Activation , SimpleRNN
from keras.models import Sequential, load_model
import MeCab
import csv
import numpy as np

CONTEXT = 4
HIDDEN_SIZE = 200
BATCH_SIZE = 128
N_ITERATIONS = 50
N_EPOCHS = 5  # the number of epochs per iteration
mecab = MeCab.Tagger('-Owakati')
EOS = '[EOS]'

def parse(s):
    """形態素解析（分かち書き）"""
    return mecab.parse(s).strip().split(' ')

def read_dataset(files):
    dataset = []
    for fpath in files:
        with open(fpath, 'r') as fin:
            for row in csv.DictReader(fin):
                ss = row['poem'].split('\\n')
                if ss[0] != '': dataset.append(parse(ss[0]) + [EOS])
    return dataset

def make_xy_pairs(dataset):
    xys = []
    for s in dataset:
        for i in range(len(s)-CONTEXT):
            xys.append((s[i:i+CONTEXT], s[i+CONTEXT]))
    return xys

def make_matrices(wd2idx, xys):
    n_wds = len(wd2idx)
    X = np.zeros((len(xys), CONTEXT, n_wds), dtype=np.bool)
    Y = np.zeros((len(xys), n_wds), dtype=np.bool)
    for i, (x, y) in enumerate(xys):
        for j, c in enumerate(x): X[i,j,wd2idx[c]] = 1
        Y[i,wd2idx[y]] = 1
    return (X, Y)

def generate_seed(seeds):
    return seeds[np.random.randint(len(seeds))]

def predict_word(wd2idx, idx2wd, model, seed):
    n_wds = len(idx2wd)
    Xt = np.zeros((1, CONTEXT, n_wds))
    for i, w in enumerate(seed):
        Xt[0,i,wd2idx[w]] = 1
    p = model.predict(Xt, verbose=0)[0]  # predicted probabilities
    y = idx2wd[np.argmax(p)]
    return y

def predict_sentence(wd2idx, idx2wd, model, seed):
    sentence = list(seed)
    for i in range(100):
        w = predict_word(wd2idx, idx2wd, model, seed)
        if w == EOS: break
        sentence.append(w)
        seed = seed[1:] + [w]
    return ''.join(sentence)

def train(wd2idx, idx2wd, dataset, X, Y):
    n_wds = X.shape[2]

    model = Sequential()
    model.add(SimpleRNN(HIDDEN_SIZE, return_sequences=False, input_shape=(CONTEXT, n_wds), unroll=True))
    model.add(Dense(n_wds, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')

    seeds = [s[0:CONTEXT] for s in dataset]
    for i in range(N_ITERATIONS):
        print('=' * 50)
        print('Iteration #{}'.format(i))
        model.fit(X, Y, batch_size=BATCH_SIZE, epochs=N_EPOCHS)
        while True:
            seed = generate_seed(seeds)
            sentence = predict_sentence(wd2idx, idx2wd, model, seed)
            if sentence not in dataset:
                print('Prediction: seed=' + ''.join(seed) + ', sentence=' + ''.join(sentence))
                break

    return model

def main(args):
    dataset = read_dataset(args.files)
    words = sorted(list(set(sum(dataset, []))))
    wd2idx = dict((c,i) for i, c in enumerate(words))
    idx2wd = dict((i,c) for i, c in enumerate(words))
    if args.model is None:
        xys = make_xy_pairs(dataset)
        (X, Y) = make_matrices(wd2idx, xys)
        model = train(wd2idx, idx2wd, dataset, X, Y)
        model.save('word_rnn.h5')
    else:
        model = load_model(args.model)
        seeds = [s[0:CONTEXT] for s in dataset]
        for j in range(5):
            while True:
                seed = generate_seed(seeds)
                sentence = predict_sentence(wd2idx, idx2wd, model, seed)
                if sentence not in dataset:
                    print('Prediction: seed=' + ''.join(seed) + ', sentence=' + ''.join(sentence))
                    break

if __name__ == '__main__':
    parser = ArgumentParser(description='Lens poem generation by Markov chain')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='CSV file (training data)')
    parser.add_argument('--model', metavar='FILE', type=str, help='Trained model file')
    args = parser.parse_args()
    main(args)
