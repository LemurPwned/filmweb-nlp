import spacy
from collections import defaultdict
from flask import request, Response
import os
import json 

nlp = spacy.load("pl_model")
data_loc = '/etc/cvoldata'


def main():
    try:
        # myHeader = request.headers['x-my-header']
        body = request.get_json()
        result = None
        try:
            reviews_loc = os.path.join(data_loc, 'reviews')
            body = os.listdir(reviews_loc)
            filenames = [os.path.join(reviews_loc, filename) for filename in body]
            result = map_filename(filenames)
        except Exception as e:
            body = e.with_traceback
    except KeyError:
        return "Header 'x-my-header' not found"
    return Response(json.dumps(result))


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
                # print(ent.label_, f"the text: {ent.text} of ent")
                entities[ent.label_].append(ent.text)
    return entities


if __name__ == "__main__":
    d = map_filename(['text_files/random_text.txt'])
    print(d)

# fission env create --spec --name python --image lemurpwned/fission-spacy --builder fission/python-builder
# fission function create --spec --name spacy --env python --src "NER.py" --entrypoint NER.main
# fission function updae --spec --name spacy --env python --src "NER.py" --entrypoint NER.main
