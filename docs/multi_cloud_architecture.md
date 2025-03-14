# Multi-Cloud Infrastructure Design

## Overview
Our multi-cloud setup leverages the free tiers of AWS, Google Cloud, and Azure to distribute the LLM fine-tuning workload efficiently.

## Architecture Diagram
AWS │ Google Cloud │ Azure
────┼─────────────┼──────
S3 │ GCS │ Blob Storage
Data │ Training │ Evaluation
EC2 │ Compute │ VM
────┴─────────────┴──────


## AWS Components
- **S3 Bucket**: Primary data storage for datasets and model checkpoints
- **EC2 Instance**: Training coordinator and lightweight inference

## Google Cloud Components
- **Google Cloud Storage**: Secondary backup for datasets
- **Compute Engine**: Primary training infrastructure with T4 GPU (using $300 credit)

## Azure Components
- **Azure Blob Storage**: Tertiary backup and model artifact storage
- **Azure VM**: Evaluation and testing environment

## Data Flow
1. Dataset is preprocessed locally and uploaded to all three cloud storage solutions
2. Training occurs primarily on GCP's T4 GPUs
3. Model checkpoints are saved to AWS S3
4. Evaluation runs on Azure VMs
5. Final model is deployed across all three platforms for fault tolerance
