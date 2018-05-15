#!/bin/sh
NEWRELIC_APP_ID=$(aws ssm get-parameter --name /site/NEWRELIC_OPENSTATES_APP_ID --with-decryption | jq -r .Parameter.Value)
NEWRELIC_API_KEY=$(aws ssm get-parameter --name /site/NEWRELIC_API_KEY --with-decryption | jq -r .Parameter.Value)
REV="deploy $(date)"
CHANGELOG=""
DESCRIPTION=""
USER="$(whoami)@$(hostname)"

curl -X POST "https://api.newrelic.com/v2/applications/$NEWRELIC_APP_ID/deployments.json" \
     -H "X-Api-Key:$NEWRELIC_API_KEY" -i \
     -H "Content-Type: application/json" \
     -d \
"{
  \"deployment\": {
    \"revision\": \"$REV\",
    \"changelog\": \"$CHANGELOG\",
    \"description\": \"$DESCRIPTION\",
    \"user\": \"$USER\"
  }
}" 
