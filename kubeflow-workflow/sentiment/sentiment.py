import pyss3
from collections import defaultdict
from flask import request, Response
import os
import json

# idotic, won't load from custom loc
pyss3.SS3.__models_folder__ = os.path.join('.', 'ss3_models')
clf = pyss3.SS3()
clf.load_model()

print(f"Using model with parameters {clf.get_hyperparameters()}")

import argparse

parser = argparse.ArgumentParser(description='Concatenate text')
parser.add_argument('--inputd', type=str, help='Input directory to read from')
parser.add_argument('--outputd', type=str, help='Output directory to save to.')
args = parser.parse_args()

print(args.inputd)
print(args.outputd)


def infer_sentiment(filenames):
    sentiments = defaultdict(list)
    for filename in filenames:
        if not filename.endswith('.txt'):
            continue
        with open(filename, 'r') as f:
            text = f.read()
        result = clf.predict(text,
                             def_cat='most-probable',
                             labels=True,
                             prep=True,
                             leave_pbar=False)
        sentiments[filename] = result
    return sentiments


rev_list = os.listdir(args.inputd)
filenames = [os.path.join(args.inputd, filename) for filename in rev_list]
result = infer_sentiment(filenames)

json.dump(result, open(os.path.join(args.outputd, 'sentiment.json'), 'w'))
