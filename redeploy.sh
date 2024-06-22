#!/bin/bash

# variables
SERVICE_NAME="google-hackathon-june-2024"
PROJECT_ID="sublime-lyceum-426907-r9"
REGION="europe-west1"
ENV_VARS="DATABASE_URL=postgresql://postgres.nemxqrrucjdjhammqvpq:Zeb0rah41Zeb0rah42@aws-0-eu-west-1.pooler.supabase.com:6543/postgres,GOOGLE_MAP_API_KEY=AIzaSyCNB7zNqVvSj_om_E2uiil2mNPb-XqqpJM"

# deploy command
gcloud run deploy $SERVICE_NAME \
    --source .                  \
    --project $PROJECT_ID       \
    --region $REGION            \
    --set-env-vars $ENV_VARS    \
    --allow-unauthenticated
