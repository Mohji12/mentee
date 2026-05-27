# Fast Docker Build Script with BuildKit
# This uses Docker BuildKit for parallel builds and better caching

$ErrorActionPreference = "Stop"

$IMAGE_NAME = "mentee"
$IMAGE_TAG = "latest"
$DOCKERFILE = "Dockerfile.fast-build"

Write-Host "🚀 Fast Docker Build with BuildKit" -ForegroundColor Green
Write-Host "====================================" -ForegroundColor Green
Write-Host ""

# Enable BuildKit for faster builds
$env:DOCKER_BUILDKIT = "1"
$env:COMPOSE_DOCKER_CLI_BUILD = "1"

Write-Host "📦 Building image with BuildKit..." -ForegroundColor Yellow
Write-Host "   This will use parallel builds and better caching" -ForegroundColor Gray
Write-Host ""

# Build with BuildKit optimizations
docker build `
    --progress=plain `
    --tag "${IMAGE_NAME}:${IMAGE_TAG}" `
    --file $DOCKERFILE `
    .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build completed successfully!" -ForegroundColor Green
    Write-Host "📍 Image: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Tag: docker tag ${IMAGE_NAME}:${IMAGE_TAG} 474833638797.dkr.ecr.ap-south-1.amazonaws.com/${IMAGE_NAME}:${IMAGE_TAG}"
    Write-Host "  2. Push: docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/${IMAGE_NAME}:${IMAGE_TAG}"
} else {
    Write-Host ""
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

