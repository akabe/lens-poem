from argparse import ArgumentParser
from keras.layers import Dense , Activation , SimpleRNN
from keras.models import Sequential, load_model
import csv
import numpy as np

CONTEXT = 10
HIDDEN_SIZE = 200
BATCH_SIZE = 128
N_ITERATIONS = 30
N_EPOCHS = 5  # the number of epochs per iteration
EOS = '$'

def read_dataset(files):
    dataset = []
    for fpath in files:
        with open(fpath, 'r') as fin:
            for row in csv.DictReader(fin):
                ss = row['poem'].split('\\n')
                if ss[0] != '': dataset.append(ss[0])
    return dataset

def make_xy_pairs(dataset):
    xys = []
    for s in dataset:
        s = s + EOS
        for i in range(len(s)-CONTEXT):
            xys.append((s[i:i+CONTEXT], s[i+CONTEXT]))
    return xys

def make_matrices(chr2idx, xys):
    n_chrs = len(chr2idx)
    X = np.zeros((len(xys), CONTEXT, n_chrs), dtype=np.bool)
    Y = np.zeros((len(xys), n_chrs), dtype=np.bool)
    for i, (x, y) in enumerate(xys):
        for j, c in enumerate(x): X[i,j,chr2idx[c]] = 1
        Y[i,chr2idx[y]] = 1
    return (X, Y)

def generate_seed(seeds):
    i = np.random.randint(len(seeds))
    return seeds[i]

def predict_char(chr2idx, idx2chr, model, seed):
    n_chrs = len(idx2chr)
    Xt = np.zeros((1, CONTEXT, n_chrs))
    for i, c in enumerate(seed):
        Xt[0,i,chr2idx[c]] = 1
    p = model.predict(Xt, verbose=0)[0]  # predicted probabilities
    y = idx2chr[np.argmax(p)]  # predict character
    return y

def predict_sentence(chr2idx, idx2chr, model, seed):
    sentence = list(seed)
    for i in range(100):
        c = predict_char(chr2idx, idx2chr, model, seed)
        if c == EOS: break
        sentence.append(c)
        seed = seed[1:] + c
    return ''.join(sentence)

def train(chr2idx, idx2chr, dataset, X, Y):
    n_chrs = X.shape[2]

    model = Sequential()
    model.add(SimpleRNN(HIDDEN_SIZE, return_sequences=False, input_shape=(CONTEXT, n_chrs), unroll=True))
    model.add(Dense(n_chrs, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam')

    seeds = [s[0:CONTEXT] for s in dataset]
    for i in range(N_ITERATIONS):
        print('=' * 50)
        print('Iteration #{}'.format(i))
        model.fit(X, Y, batch_size=BATCH_SIZE, epochs=N_EPOCHS)
        while True:
            seed = generate_seed(seeds)
            sentence = predict_sentence(chr2idx, idx2chr, model, seed)
            if sentence not in dataset:
                print('Prediction: seed=' + seed + ', sentence=' + sentence)
                break

    return model

def main(args):
    dataset = read_dataset(args.files)
    chrs = sorted(list(set(''.join(dataset) + EOS)))
    chr2idx = dict((c,i) for i, c in enumerate(chrs))
    idx2chr = dict((i,c) for i, c in enumerate(chrs))
    if args.model is None:
        xys = make_xy_pairs(dataset)
        (X, Y) = make_matrices(chr2idx, xys)
        model = train(chr2idx, idx2chr, dataset, X, Y)
        model.save('char_rnn.h5')
    else:
        model = load_model(args.model)
        seeds = [s[0:CONTEXT] for s in dataset]
        for j in range(5):
            while True:
                seed = generate_seed(seeds)
                sentence = predict_sentence(chr2idx, idx2chr, model, seed)
                if sentence not in dataset:
                    print('seed=' + seed + ', sentence=' + sentence)
                    break

if __name__ == '__main__':
    parser = ArgumentParser(description='Lens poem generation by Markov chain')
    parser.add_argument('files', metavar='FILE', type=str, nargs='+', help='CSV file (training data)')
    parser.add_argument('--model', metavar='FILE', type=str, help='Trained model file')
    args = parser.parse_args()
    main(args)
