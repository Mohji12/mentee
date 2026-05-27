# Docker Build Optimization Guide

## Current Problem
Docker builds are taking **25+ minutes**, especially on pip install step (1392 seconds).

## Root Causes
1. **Heavy packages**: pandas, numpy, plotly, kaleido, chromium
2. **No pip cache**: Using `--no-cache-dir` prevents reuse
3. **Verbose output**: `-v` flag slows down pip
4. **Multiple RUN layers**: Each RUN creates a new layer
5. **Installing to current directory**: `-t .` can be slower

## Solutions

### Option 1: Use Optimized Dockerfile (Recommended)
```bash
docker build -f Dockerfile.optimized -t mentee:latest .
```

**Improvements:**
- ✅ Uses pip cache (`--cache-dir /tmp/pip-cache`)
- ✅ Removed verbose flag (`-v`)
- ✅ Combined cleanup steps
- ✅ Better layer caching

### Option 2: Use Fast Dockerfile (Minimal)
```bash
docker build -f Dockerfile.fast -t mentee:latest .
```

**Improvements:**
- ✅ Minimal layers (faster)
- ✅ Combined operations
- ✅ Automatic cleanup

### Option 3: Build with BuildKit (Faster)
```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build
docker build -f Dockerfile.optimized -t mentee:latest .
```

**For Windows PowerShell:**
```powershell
$env:DOCKER_BUILDKIT=1
docker build -f Dockerfile.optimized -t mentee:latest .
```

### Option 4: Use Docker Build Cache
```bash
# Build with cache mount (faster pip installs)
docker build --cache-from mentee:latest -f Dockerfile.optimized -t mentee:latest .
```

## Build Time Comparison

| Dockerfile | Estimated Time | Notes |
|------------|---------------|-------|
| `Dockerfile` (current) | 25-30 min | No cache, verbose |
| `Dockerfile.optimized` | 15-20 min | With pip cache |
| `Dockerfile.fast` | 12-18 min | Minimal layers |
| With BuildKit | 10-15 min | Parallel builds |

## Additional Optimizations

### 1. Split Requirements (Advanced)
Create `requirements-core.txt` and `requirements-optional.txt`:

```bash
# Install core packages first (changes less often)
docker build --target core -f Dockerfile.multi-stage -t mentee:core .

# Then install optional packages
docker build --target full -f Dockerfile.multi-stage -t mentee:latest .
```

### 2. Use Pre-built Base Image
If you rebuild frequently, create a base image with system packages:

```dockerfile
# Dockerfile.base
FROM public.ecr.aws/lambda/python:3.11
RUN yum install -y [packages] && yum clean all
RUN pip install --upgrade pip setuptools wheel
```

```bash
# Build base once
docker build -f Dockerfile.base -t mentee-base:latest .

# Use base for faster builds
FROM mentee-base:latest
COPY requirements.txt .
RUN pip install -r requirements.txt -t .
```

### 3. Build on EC2/Cloud Build
If building locally is slow, use AWS CodeBuild or EC2:

```bash
# On EC2 with better network
aws ecr get-login-password --region ap-south-1 | \
    docker login --username AWS --password-stdin \
    474833638797.dkr.ecr.ap-south-1.amazonaws.com

docker build -f Dockerfile.optimized -t mentee:latest .
```

### 4. Use Docker Buildx (Parallel Builds)
```bash
# Create builder
docker buildx create --name mybuilder --use

# Build with parallel jobs
docker buildx build --platform linux/amd64 \
    -f Dockerfile.optimized \
    -t mentee:latest \
    --load .
```

## Quick Commands

### Fastest Build (Recommended)
```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Build optimized version
docker build -f Dockerfile.optimized -t mentee:latest .

# Tag and push
docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

### One-Line (PowerShell)
```powershell
$env:DOCKER_BUILDKIT=1; docker build -f Dockerfile.optimized -t mentee:latest .; docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest; docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

## Monitoring Build Progress

### Check Build Progress
```bash
# In another terminal
docker ps

# Check Docker logs
docker events
```

### Build with Progress Output
```bash
docker build --progress=plain -f Dockerfile.optimized -t mentee:latest .
```

## Troubleshooting

### If build still slow:
1. **Check internet speed**: Slow downloads affect pip
2. **Use local pip cache**: Mount local cache directory
3. **Reduce packages**: Remove unused dependencies
4. **Use pre-compiled wheels**: Some packages build from source

### If build fails:
```bash
# Build with no cache
docker build --no-cache -f Dockerfile.optimized -t mentee:latest .

# Check intermediate layers
docker history mentee:latest
```

## Expected Results

After optimization:
- **First build**: 15-20 minutes (still downloads packages)
- **Subsequent builds**: 5-10 minutes (with cache)
- **Code-only changes**: 1-2 minutes (only rebuilds app layer)

