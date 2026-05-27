# Working Docker Build Script
# Fixes BuildKit/Buildx EOF error

$ErrorActionPreference = "Stop"

$IMAGE_NAME = "mentee"
$IMAGE_TAG = "latest"

Write-Host "🔨 Docker Build (Fixed)" -ForegroundColor Green
Write-Host "=======================" -ForegroundColor Green
Write-Host ""

# Solution 1: Disable BuildKit (Most Reliable)
Write-Host "Using standard Docker builder (BuildKit disabled)..." -ForegroundColor Yellow
$env:DOCKER_BUILDKIT = "0"
$env:COMPOSE_DOCKER_CLI_BUILD = "0"

Write-Host ""
Write-Host "Building image..." -ForegroundColor Yellow
docker build --tag "${IMAGE_NAME}:${IMAGE_TAG}" .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host "📍 Image: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Cyan
    Write-Host ""
    
    # Show image info
    docker images "${IMAGE_NAME}:${IMAGE_TAG}" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
    
    Write-Host ""
    Write-Host "Ready to tag and push:" -ForegroundColor Yellow
    Write-Host "  docker tag ${IMAGE_NAME}:${IMAGE_TAG} 474833638797.dkr.ecr.ap-south-1.amazonaws.com/${IMAGE_NAME}:${IMAGE_TAG}"
    Write-Host "  docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/${IMAGE_NAME}:${IMAGE_TAG}"
} else {
    Write-Host ""
    Write-Host "❌ Build failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Try these fixes:" -ForegroundColor Yellow
    Write-Host "  1. Restart Docker Desktop"
    Write-Host "  2. Run: docker system prune"
    Write-Host "  3. Check Docker Desktop settings > General > Use Docker Compose V2 (disable if enabled)"
    exit 1
}

