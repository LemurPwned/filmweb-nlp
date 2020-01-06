import pyss3
from collections import defaultdict
from flask import request, Response
import os
import json


data_loc = '/etc/cvoldata'
# idotic, won't load from custom loc
pyss3.SS3.__models_folder__ = os.path.join(data_loc, 'ss3_models')
clf = pyss3.SS3()
clf.load_model()

print(f"Using model with parameters {clf.get_hyperparameters()}")

def main():
    try:
        # myHeader = request.headers['x-my-header']
        body = request.get_json()
        result = None
        try:
            reviews_loc = os.path.join(data_loc, 'reviews')
            body = os.listdir(reviews_loc)
            filenames = [os.path.join(reviews_loc, filename) for filename in body]
            result = infer_sentiment(filenames)
        except Exception as e:
            body = e.with_traceback
    except KeyError:
        return "Header 'x-my-header' not found"
    return Response(json.dumps(result))

def infer_sentiment(filenames):
    sentiments = defaultdict(list)
    for filename in filenames:
        if not filename.endswith('.txt'):
            continue
        with open(filename, 'r') as f:
            text = f.read()
        result = clf.predict(text,
            def_cat='unknown',
            labels=True,
            prep=True,
            leave_pbar=False)
        sentiments[filename] = result
    return sentiments