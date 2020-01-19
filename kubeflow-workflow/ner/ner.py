import spacy
from collections import defaultdict
import os
import json
import sys

import argparse

parser = argparse.ArgumentParser(description='Concatenate text')
parser.add_argument('--inputd', type=str, help='Input directory to read from')
parser.add_argument('--outputd', type=str, help='Output directory to save to.')
args = parser.parse_args()

print(args.inputd)
print(args.outputd)

nlp = spacy.load("pl_model")


def map_filename(filenames):
    entities = defaultdict(list)
    for filename in filenames:
        if not filename.endswith('.txt'):
            continue
        with open(filename, 'r') as f:
            text = f.read()
        doc = nlp(text)
        for ent in doc.ents:
            if ent.text.replace(" ", "").replace("\n", "").strip() != "":
                entities[ent.label_].append(ent.text)
    return entities


rev_list = os.listdir(args.inputd)
filenames = [os.path.join(args.inputd, filename) for filename in rev_list]
result = map_filename(filenames)

json.dump(result, open(os.path.join(args.outputd, 'ner.json'), 'w'))
