#!/bin/bash

# Set your GitHub credentials
GITHUB_USERNAME="edge-surv"
GITHUB_TOKEN="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"

# Log in to GHCR
echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$GITHUB_USERNAME" --password-stdin

# Pull the Docker image
sudo docker pull ghcr.io/edge-surv/deep-edge-surv-api:latest


