# Standard Docker Build (No BuildKit)
# Use this if BuildKit causes issues

$ErrorActionPreference = "Stop"

$IMAGE_NAME = "mentee"
$IMAGE_TAG = "latest"

Write-Host "🔨 Standard Docker Build" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
Write-Host ""

# Disable BuildKit completely
$env:DOCKER_BUILDKIT = "0"
$env:COMPOSE_DOCKER_CLI_BUILD = "0"

Write-Host "Building without BuildKit..." -ForegroundColor Yellow
Write-Host ""

docker build --tag "${IMAGE_NAME}:${IMAGE_TAG}" .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
    Write-Host "📍 Image: ${IMAGE_NAME}:${IMAGE_TAG}" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

