# Fix Docker Buildx Issues

Write-Host "🔧 Fixing Docker Buildx Issues" -ForegroundColor Green
Write-Host "==============================" -ForegroundColor Green
Write-Host ""

# Solution 1: Use default builder (not Buildx)
Write-Host "Option 1: Using default Docker builder..." -ForegroundColor Yellow
$env:DOCKER_BUILDKIT = "0"

docker build --tag "mentee:latest" .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build successful with default builder!" -ForegroundColor Green
    exit 0
}

Write-Host ""
Write-Host "Trying alternative solution..." -ForegroundColor Yellow

# Solution 2: Reset Buildx and use --load
Write-Host "Option 2: Resetting Buildx..." -ForegroundColor Yellow
docker buildx rm default 2>$null
docker buildx rm desktop-linux 2>$null

# Use standard docker build
$env:DOCKER_BUILDKIT = "0"
docker build --tag "mentee:latest" .

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build successful!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Build still failing. Please:" -ForegroundColor Red
    Write-Host "  1. Restart Docker Desktop"
    Write-Host "  2. Run: docker system prune -a"
    Write-Host "  3. Try building again"
}

