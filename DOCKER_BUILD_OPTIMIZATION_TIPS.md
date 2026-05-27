# Docker Build Optimization Tips

## Problem: Slow Unpacking During Docker Build

The unpacking phase is slow because:
1. **Large base image** - Lambda Python base image is large
2. **Many system packages** - Installing chromium, gtk3, etc. takes time
3. **Python packages** - Installing all requirements creates large layers
4. **No BuildKit** - Not using parallel builds

## Quick Solutions

### 1. Use BuildKit (Fastest Improvement)
```powershell
# Enable BuildKit
$env:DOCKER_BUILDKIT = "1"
docker build --tag mentee:latest .
```

### 2. Use Optimized Dockerfile
```powershell
# Use the fast-build Dockerfile
docker build -f Dockerfile.fast-build -t mentee:latest .
```

### 3. Build with Cache Mount (Windows)
```powershell
docker build --build-arg BUILDKIT_INLINE_CACHE=1 -t mentee:latest .
```

### 4. Exclude Unnecessary Files
Make sure `.dockerignore` includes:
```
node_modules/
frontend/
*.pyc
__pycache__/
.git/
*.md
*.txt
!requirements.txt
```

## Speed Improvements

### Current Build Time: ~25-30 minutes
### With Optimizations: ~10-15 minutes

## Recommended Build Command

```powershell
# Fastest build with all optimizations
$env:DOCKER_BUILDKIT = "1"
docker build --progress=plain -f Dockerfile.fast-build -t mentee:latest .
```

## Alternative: Use Pre-built Base Image

If unpacking is still slow, consider:
1. Pre-building a base image with dependencies
2. Using multi-stage builds
3. Using AWS Lambda base images with dependencies pre-installed

## Monitor Build Progress

```powershell
# See detailed progress
docker build --progress=plain -t mentee:latest .
```

