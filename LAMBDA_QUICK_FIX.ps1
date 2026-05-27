# Quick fix script for Windows PowerShell
# This fixes the "uvicorn not found" error

$ErrorActionPreference = "Stop"

$AWS_ACCOUNT_ID = "474833638797"
$ECR_REPO_NAME = "mentee"
$AWS_REGION = "ap-south-1"
$IMAGE_TAG = "latest"
$ECR_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

Write-Host "🔧 Fixing Lambda deployment..." -ForegroundColor Green
Write-Host "Using Dockerfile (Lambda-compatible) instead of Dockerfile.standard" -ForegroundColor Yellow
Write-Host ""

# Step 1: Login
Write-Host "📝 Logging into ECR..." -ForegroundColor Yellow
aws ecr get-login-password --region $AWS_REGION | `
    docker login --username AWS --password-stdin $ECR_URI

# Step 2: Build with correct Dockerfile
Write-Host "🔨 Building Lambda-compatible image..." -ForegroundColor Yellow
docker build -f Dockerfile -t "${ECR_REPO_NAME}:${IMAGE_TAG}" .

# Step 3: Tag
Write-Host "🏷️  Tagging image..." -ForegroundColor Yellow
docker tag "${ECR_REPO_NAME}:${IMAGE_TAG}" "${ECR_URI}:${IMAGE_TAG}"

# Step 4: Push
Write-Host "📤 Pushing to ECR..." -ForegroundColor Yellow
docker push "${ECR_URI}:${IMAGE_TAG}"

Write-Host ""
Write-Host "✅ Fixed! Image pushed successfully." -ForegroundColor Green
Write-Host "📍 Image URI: ${ECR_URI}:${IMAGE_TAG}" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  Make sure your Lambda function is configured to use this image URI" -ForegroundColor Yellow





