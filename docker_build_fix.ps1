# Fixed Docker Build Script
# Resolves BuildKit/Buildx issues

$ErrorActionPreference = "Stop"

$IMAGE_NAME = "mentee"
$IMAGE_TAG = "latest"

Write-Host "🔧 Docker Build Fix" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host ""

# Check Docker is running
Write-Host "📋 Checking Docker..." -ForegroundColor Yellow
docker ps | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Docker is running" -ForegroundColor Green
Write-Host ""

# Option 1: Build with --load flag (for Buildx)
Write-Host "🔨 Building with --load flag (Buildx compatible)..." -ForegroundColor Yellow
Write-Host ""

# Disable BuildKit to use standard builder (more reliable)
$env:DOCKER_BUILDKIT = "0"

docker build --tag "${IMAGE_NAME}:${IMAGE_TAG}" .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build completed successfully!" -ForegroundColor Green
    Write-Host "📍 Image: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Cyan
    Write-Host ""
    
    # Verify image exists
    docker images "${IMAGE_NAME}:${IMAGE_TAG}"
    
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "  1. Tag: docker tag ${IMAGE_NAME}:${IMAGE_TAG} 474833638797.dkr.ecr.ap-south-1.amazonaws.com/${IMAGE_NAME}:${IMAGE_TAG}"
    Write-Host "  2. Push: docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/${IMAGE_NAME}:${IMAGE_TAG}"
} else {
    Write-Host ""
    Write-Host "❌ Build failed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Yellow
    Write-Host "  1. Make sure Docker Desktop is running"
    Write-Host "  2. Try: docker system prune -a (clean up)"
    Write-Host "  3. Restart Docker Desktop"
    exit 1
}

