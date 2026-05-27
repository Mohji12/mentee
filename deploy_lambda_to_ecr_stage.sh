#!/bin/bash

# ECR Configuration for Lambda
AWS_ACCOUNT_ID="474833638797"
ECR_REPO_NAME="stage"
AWS_REGION="us-east-1"
IMAGE_TAG="latest"

# ECR Repository URI
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

echo "🚀 Starting Lambda ECR deployment process..."

# Step 1: Login to ECR
echo "📝 Logging into ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_URI}

if [ $? -ne 0 ]; then
    echo "❌ Failed to login to ECR"
    exit 1
fi

# Step 2: Build Docker image with Lambda Dockerfile
echo "🔨 Building Docker image for Lambda (using Dockerfile, not Dockerfile.standard)..."
docker build -f Dockerfile -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

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
    echo "✅ Successfully pushed Lambda image to ECR!"
    echo "📍 Image URI: ${ECR_URI}:${IMAGE_TAG}"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Go to AWS Lambda Console"
    echo "2. Update your Lambda function to use this image: ${ECR_URI}:${IMAGE_TAG}"
    echo "3. Handler field: Leave EMPTY (container images don't use handler field)"
    echo "4. The CMD in Dockerfile already points to: app.main.handler"
else
    echo "❌ Failed to push image to ECR"
    exit 1
fi

echo "🎉 Lambda deployment completed successfully!"



