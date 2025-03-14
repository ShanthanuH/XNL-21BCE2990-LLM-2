#!/bin/bash
# AWS Setup Script

# Install AWS CLI
pip install awscli

# Configure AWS (you'll need to enter your credentials)
aws configure

# Create S3 bucket for data storage
aws s3 mb s3://xnl-llm-task-data

# Upload dataset to S3
aws s3 cp ./data s3://xnl-llm-task-data/imdb/ --recursive

echo "AWS setup complete!"
