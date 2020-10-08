#!/bin/bash
set -ex

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 189670762819.dkr.ecr.us-east-1.amazonaws.com
docker build -t widgets .
docker tag widgets:latest 189670762819.dkr.ecr.us-east-1.amazonaws.com/widgets:latest
docker push 189670762819.dkr.ecr.us-east-1.amazonaws.com/widgets:latest

if [ $1 ]
then
  docker tag widgets:latest 189670762819.dkr.ecr.us-east-1.amazonaws.com/widgets:$1
  docker push 189670762819.dkr.ecr.us-east-1.amazonaws.com/widgets:$1
fi
