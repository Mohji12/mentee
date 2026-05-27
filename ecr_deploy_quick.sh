#!/bin/bash

# Quick ECR Deployment Script
# AWS Account ID: 474833638797
# Repository: mentee
# Region: ap-south-1

set -e  # Exit on error

# Configuration
AWS_ACCOUNT_ID="474833638797"
ECR_REPO_NAME="mentee"
AWS_REGION="ap-south-1"
IMAGE_TAG="latest"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "🚀 Starting ECR deployment..."
echo "📍 Repository: ${ECR_URI}"
echo ""

# Step 1: Login to ECR
echo "📝 Step 1: Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_URI}

if [ $? -ne 0 ]; then
    echo "❌ Failed to login to ECR"
    exit 1
fi
echo "✅ Logged in successfully"
echo ""

# Step 2: Build Docker image (using Dockerfile for Lambda)
echo "🔨 Step 2: Building Docker image for Lambda..."
docker build -f Dockerfile -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image"
    exit 1
fi
echo "✅ Image built successfully"
echo ""

# Step 3: Tag image for ECR
echo "🏷️  Step 3: Tagging image for ECR..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}
echo "✅ Image tagged successfully"
echo ""

# Step 4: Push to ECR
echo "📤 Step 4: Pushing image to ECR..."
docker push ${ECR_URI}:${IMAGE_TAG}

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed image to ECR!"
    echo "📍 Image URI: ${ECR_URI}:${IMAGE_TAG}"
    echo ""
    echo "🎉 Deployment completed successfully!"
else
    echo "❌ Failed to push image to ECR"
    exit 1
fi

