apply:
	fission spec apply --wait
create:
	fission function create --spec --name spacy --env python --src "ner/*" --entrypoint ner.main
clean:
	fission fn delete --name spacy
	fission env delete --name python
	
