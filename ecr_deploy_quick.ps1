# Quick ECR Deployment Script for Windows PowerShell
# AWS Account ID: 474833638797
# Repository: mentee
# Region: ap-south-1

$ErrorActionPreference = "Stop"

# Configuration
$AWS_ACCOUNT_ID = "474833638797"
$ECR_REPO_NAME = "mentee"
$AWS_REGION = "ap-south-1"
$IMAGE_TAG = "latest"
$ECR_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

Write-Host "🚀 Starting ECR deployment..." -ForegroundColor Green
Write-Host "📍 Repository: ${ECR_URI}" -ForegroundColor Cyan
Write-Host ""

# Step 1: Login to ECR
Write-Host "📝 Step 1: Logging into ECR..." -ForegroundColor Yellow
$loginResult = aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to login to ECR" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Logged in successfully" -ForegroundColor Green
Write-Host ""

# Step 2: Build Docker image (using Dockerfile for Lambda)
Write-Host "🔨 Step 2: Building Docker image for Lambda..." -ForegroundColor Yellow
docker build -f Dockerfile -t "${ECR_REPO_NAME}:${IMAGE_TAG}" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Image built successfully" -ForegroundColor Green
Write-Host ""

# Step 3: Tag image for ECR
Write-Host "🏷️  Step 3: Tagging image for ECR..." -ForegroundColor Yellow
docker tag "${ECR_REPO_NAME}:${IMAGE_TAG}" "${ECR_URI}:${IMAGE_TAG}"
Write-Host "✅ Image tagged successfully" -ForegroundColor Green
Write-Host ""

# Step 4: Push to ECR
Write-Host "📤 Step 4: Pushing image to ECR..." -ForegroundColor Yellow
docker push "${ECR_URI}:${IMAGE_TAG}"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Successfully pushed image to ECR!" -ForegroundColor Green
    Write-Host "📍 Image URI: ${ECR_URI}:${IMAGE_TAG}" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to push image to ECR" -ForegroundColor Red
    exit 1
}

