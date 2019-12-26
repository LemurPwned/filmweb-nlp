#!/bin/sh
pip3 install -r ${SRC_PKG}/requirements.txt -t ${SRC_PKG} && cp -r ${SRC_PKG} ${DEPLOY_PKG}
python3 -m spacy download en

# fission package create --sourcearchive demo.zip --env python --buildcmd "./build.sh" --name demo 
# fission package create --sourcearchive demo.zip --env pythonsrc --buildcmd "./build.sh"
# fission fn create --name nerpy --env python-spacy --entrypoint "NER.main" --code NER.py

fission route create --url /file --function nerpy --method POST --name file 

curl -

fission env update --name python-spacy --image lemurpwned/fission-spacy
fission fn update --name nerpy --env python-spacy --entrypoint "NER.main" --code NER.py