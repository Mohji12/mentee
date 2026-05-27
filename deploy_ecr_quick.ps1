# Quick ECR Deployment Script (PowerShell)
# AWS Account: 474833638797
# Repository: mentee
# Region: ap-south-1

param(
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

$AWS_ACCOUNT_ID = "474833638797"
$ECR_REPO_NAME = "mentee"
$AWS_REGION = "ap-south-1"
$ECR_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

Write-Host "🚀 ECR Deployment" -ForegroundColor Green
Write-Host "=================="
Write-Host "Account ID: $AWS_ACCOUNT_ID"
Write-Host "Repository: $ECR_REPO_NAME"
Write-Host "Region: $AWS_REGION"
Write-Host "Tag: $ImageTag"
Write-Host "URI: ${ECR_URI}:${ImageTag}"
Write-Host ""

# Step 1: Login
Write-Host "📝 Logging into ECR..." -ForegroundColor Yellow
$password = aws ecr get-login-password --region $AWS_REGION
$password | docker login --username AWS --password-stdin $ECR_URI

# Step 2: Build
Write-Host "🔨 Building image..." -ForegroundColor Yellow
docker build -t "${ECR_REPO_NAME}:${ImageTag}" .

# Step 3: Tag
Write-Host "🏷️  Tagging image..." -ForegroundColor Yellow
docker tag "${ECR_REPO_NAME}:${ImageTag}" "${ECR_URI}:${ImageTag}"

# Step 4: Push
Write-Host "📤 Pushing to ECR..." -ForegroundColor Yellow
docker push "${ECR_URI}:${ImageTag}"

Write-Host ""
Write-Host "✅ Success!" -ForegroundColor Green
Write-Host "📍 Image: ${ECR_URI}:${ImageTag}" -ForegroundColor Cyan

