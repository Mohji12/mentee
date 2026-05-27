#!/bin/bash

# Quick ECR Deployment Script
# AWS Account: 474833638797
# Repository: mentee
# Region: ap-south-1

set -e  # Exit on error

AWS_ACCOUNT_ID="474833638797"
ECR_REPO_NAME="mentee"
AWS_REGION="ap-south-1"
IMAGE_TAG="${1:-latest}"  # Use first argument as tag, default to 'latest'

ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "🚀 ECR Deployment"
echo "=================="
echo "Account ID: ${AWS_ACCOUNT_ID}"
echo "Repository: ${ECR_REPO_NAME}"
echo "Region: ${AWS_REGION}"
echo "Tag: ${IMAGE_TAG}"
echo "URI: ${ECR_URI}:${IMAGE_TAG}"
echo ""

# Step 1: Login
echo "📝 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_URI}

# Step 2: Build
echo "🔨 Building image..."
docker build -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

# Step 3: Tag
echo "🏷️  Tagging image..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}

# Step 4: Push
echo "📤 Pushing to ECR..."
docker push ${ECR_URI}:${IMAGE_TAG}

echo ""
echo "✅ Success!"
echo "📍 Image: ${ECR_URI}:${IMAGE_TAG}"

