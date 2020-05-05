#!/bin/sh
set -e
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES

NEWRELIC_APP_ID=$(aws ssm get-parameter --name /site/NEWRELIC_OPENSTATES_APP_ID --with-decryption | jq -r .Parameter.Value)
NEWRELIC_API_KEY=$(aws ssm get-parameter --name /site/NEWRELIC_API_KEY --with-decryption | jq -r .Parameter.Value)
SENTRY_RELEASE_ENDPOINT=$(aws ssm get-parameter --name /site/SENTRY_RELEASE_ENDPOINT --with-decryption | jq -r .Parameter.Value)
REV="deploy $(date)"
CHANGELOG=""
DESCRIPTION=""
USER="$(whoami)@$(hostname)"

ansible-playbook openstates.yml -i inventory/ 

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

curl $SENTRY_RELEASE_ENDPOINT \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{"version": "$REV"}'
