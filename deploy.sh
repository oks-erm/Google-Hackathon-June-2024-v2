#!/bin/bash

# get env variables
if [ -f .env ]; then
  export $(grep -v '^#' .env | xargs)
else
  echo "Error: .env file not found. Please create a .env file with the required environment variables."
  exit 1
fi

# variables
SERVICE_NAME="sublime-lyceum-426907-r9"
REGION="europe-west1"
ENV_VARS=$(grep -v '^#' .env | xargs | sed 's/ /,/g')

# update requirements
pip install -r requirements.txt > /dev/null 2>&1

# deploy command
gcloud run deploy $SERVICE_NAME \
    --source .                  \
    --region $REGION            \
    --set-env-vars $ENV_VARS    \
    --allow-unauthenticated
