# Lambda Deployment Fix

## Problem
Error: `Runtime.InvalidEntrypoint - exec: "uvicorn": executable file not found in $PATH`

## Root Cause
You used `Dockerfile.standard` which has `CMD ["uvicorn", ...]` - this doesn't work in Lambda. Lambda needs a handler function, not uvicorn.

## Solution

### Option 1: Use the Correct Dockerfile (Recommended)

**For Lambda deployment, use `Dockerfile` (not `Dockerfile.standard`):**

```bash
# Build with Lambda Dockerfile
docker build -f Dockerfile -t mentee:latest .

# Tag
docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest

# Push
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

### Option 2: Quick Fix - Rebuild and Push

```bash
# Login
aws ecr get-login-password --region ap-south-1 | \
    docker login --username AWS --password-stdin \
    474833638797.dkr.ecr.ap-south-1.amazonaws.com

# Build with correct Dockerfile
docker build -f Dockerfile -t mentee:latest .

# Tag
docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest

# Push
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

## Lambda Configuration

After pushing the image, configure your Lambda function:

1. **Handler:** Leave empty (container images don't use handler field)
2. **Image URI:** `474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest`
3. **Runtime:** Container image (not Python runtime)

## Verify Handler is Correct

Your `app/main.py` has:
```python
handler = Mangum(app)
```

Your `Dockerfile` has:
```dockerfile
CMD ["app.main.handler"]
```

This is correct! The handler path `app.main.handler` means:
- Module: `app.main`
- Function: `handler`

## Key Differences

| Dockerfile | Use Case | CMD |
|------------|----------|-----|
| `Dockerfile` | **Lambda** | `CMD ["app.main.handler"]` |
| `Dockerfile.standard` | ECS/EC2/Other | `CMD ["uvicorn", "app.main:app", ...]` |

## Updated Scripts

The deployment scripts have been updated to use `Dockerfile` instead of `Dockerfile.standard`.

Run:
```bash
./ecr_deploy_quick.sh
```

Or on Windows:
```powershell
.\ecr_deploy_quick.ps1
```





