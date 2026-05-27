#!/bin/bash

# ECR Configuration
AWS_ACCOUNT_ID="941377152660"
ECR_REPO_NAME="jgi_menteetracker"
AWS_REGION="ap-south-1"
IMAGE_TAG="latest"

# ECR Repository URI
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "🚀 Starting ECR deployment process..."

# Step 1: Login to ECR
echo "📝 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

if [ $? -ne 0 ]; then
    echo "❌ Failed to login to ECR"
    exit 1
fi

# Step 2: Build Docker image
echo "🔨 Building Docker image..."
docker build -f Dockerfile.standard -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image"
    exit 1
fi

# Step 3: Tag image for ECR
echo "🏷️  Tagging image for ECR..."
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}

# Step 4: Push to ECR
echo "📤 Pushing image to ECR..."
docker push ${ECR_URI}:${IMAGE_TAG}

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed image to ECR!"
    echo "📍 Image URI: ${ECR_URI}:${IMAGE_TAG}"
else
    echo "❌ Failed to push image to ECR"
    exit 1
fi

echo "🎉 Deployment completed successfully!"





