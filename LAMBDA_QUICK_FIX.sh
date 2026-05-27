#!/bin/bash

# Quick fix script to rebuild and push Lambda-compatible image
# This fixes the "uvicorn not found" error

set -e

AWS_ACCOUNT_ID="474833638797"
ECR_REPO_NAME="mentee"
AWS_REGION="ap-south-1"
IMAGE_TAG="latest"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "🔧 Fixing Lambda deployment..."
echo "Using Dockerfile (Lambda-compatible) instead of Dockerfile.standard"
echo ""

# Step 1: Login
echo "📝 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_URI}

# Step 2: Build with correct Dockerfile
echo "🔨 Building Lambda-compatible image..."
docker build -f Dockerfile -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

# Step 3: Tag
echo "🏷️  Tagging image..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}

# Step 4: Push
echo "📤 Pushing to ECR..."
docker push ${ECR_URI}:${IMAGE_TAG}

echo ""
echo "✅ Fixed! Image pushed successfully."
echo "📍 Image URI: ${ECR_URI}:${IMAGE_TAG}"
echo ""
echo "⚠️  Make sure your Lambda function is configured to use this image URI"





