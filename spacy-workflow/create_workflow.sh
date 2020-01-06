#!/usr/bin/env bash

fission function create --name nlp-flow --env workflow --src workflow.wf.yaml
fission route create --method GET --url /nlp-flow --function nlp-flow --name nlp-flow


# export FISSION_ROUTER=$(minikube ip):$(kubectl -n fission get svc router -o jsonpath='{...nodePort}')