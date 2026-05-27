# ECR Configuration
$AWS_ACCOUNT_ID = "474833638797"
$ECR_REPO_NAME = "stage"
$AWS_REGION = "us-east-1"
$IMAGE_TAG = "latest"

# ECR Repository URI
$ECR_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

Write-Host "🚀 Starting ECR deployment process..." -ForegroundColor Cyan

# Step 1: Login to ECR
Write-Host "📝 Logging into ECR..." -ForegroundColor Yellow
$loginCommand = aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_URI

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to login to ECR" -ForegroundColor Red
    exit 1
}

# Step 2: Build Docker image
Write-Host "🔨 Building Docker image..." -ForegroundColor Yellow
docker build -f Dockerfile.standard -t "${ECR_REPO_NAME}:${IMAGE_TAG}" .

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Docker image" -ForegroundColor Red
    exit 1
}

# Step 3: Tag image for ECR
Write-Host "🏷️  Tagging image for ECR..." -ForegroundColor Yellow
docker tag "${ECR_REPO_NAME}:${IMAGE_TAG}" "${ECR_URI}:${IMAGE_TAG}"

# Step 4: Push to ECR
Write-Host "📤 Pushing image to ECR..." -ForegroundColor Yellow
docker push "${ECR_URI}:${IMAGE_TAG}"

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Successfully pushed image to ECR!" -ForegroundColor Green
    Write-Host "📍 Image URI: ${ECR_URI}:${IMAGE_TAG}" -ForegroundColor Green
} else {
    Write-Host "❌ Failed to push image to ECR" -ForegroundColor Red
    exit 1
}

Write-Host "🎉 Deployment completed successfully!" -ForegroundColor Green



