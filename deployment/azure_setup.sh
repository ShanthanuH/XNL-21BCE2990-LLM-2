#!/bin/bash
# Azure Setup Script

# Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Login to Azure
az login

# Create resource group
az group create --name xnl-llm-task --location eastus

# Create storage account
az storage account create \
    --name xnlllmtaskstorage \
    --resource-group xnl-llm-task \
    --location eastus \
    --sku Standard_LRS

# Create storage container
az storage container create \
    --name dataset \
    --account-name xnlllmtaskstorage

echo "Azure setup complete!"
