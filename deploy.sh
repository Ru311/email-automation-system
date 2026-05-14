#!/bin/bash

IMAGE="asia-south1-docker.pkg.dev/email-automation-clean/email-automation/email-automation"

echo "🐳 Building & pushing..."
docker buildx build --platform linux/amd64 -t $IMAGE --push .

echo "🚀 Deploying..."
gcloud run deploy email-automation --image $IMAGE --region asia-south1

echo "✅ Done"