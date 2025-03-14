#!/bin/bash
# Google Cloud Setup Script

# Install Google Cloud SDK
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-367.0.0-linux-x86_64.tar.gz
tar -xf google-cloud-sdk-367.0.0-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh

# Initialize GCP (you'll need to log in)
gcloud init

# Create GCS bucket
gsutil mb gs://xnl-llm-task-data

# Upload dataset to GCS
gsutil -m cp -r ./data gs://xnl-llm-task-data/imdb/

echo "Google Cloud setup complete!"
