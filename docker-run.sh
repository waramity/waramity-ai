#!/bin/bash
app="docker.waramity-ai"
docker build -t ${app} .
docker run -d -p 56729:80 \
  --link waramity-mongo:mongo \
  --name=${app} \
  -v $PWD:/app ${app}
