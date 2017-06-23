#!/bin/sh
NEWRELIC_APP_ID=$(credstash get newrelic.OPENSTATES_APP_ID)
NEWRELIC_API_KEY=$(credstash get newrelic.API_KEY)
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
