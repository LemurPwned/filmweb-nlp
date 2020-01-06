all: ner sentiment workflow
	echo "HELLO"

deleteall: 
	fission fn delete --name sentiment
	fission fn delete --name ner 
	fission fn delete --name nlp-workflow

sentiment:
	cd spacy-workflow/sentiment-spec && fission spec apply --wait

ner:
	cd spacy-workflow/ner-spec && fission spec apply --wait

workflow:
	cd spacy-workflow/ && fission function update --name nlp-flow --env workflow --src workflow.wf.yaml

	# ./spacy-workflow/create_workflow.sh