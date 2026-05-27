# Lambda Deployment Fix for Stage Repository

## Problem
```
Error: exec: "uvicorn": executable file not found in $PATH
Runtime.InvalidEntrypoint
```

## Root Cause
You're using `Dockerfile.standard` which has `CMD ["uvicorn", ...]` - this doesn't work in Lambda. Lambda needs a handler function, not uvicorn.

## Solution

### Use the Correct Dockerfile for Lambda

**For Lambda deployment, use `Dockerfile` (NOT `Dockerfile.standard`):**

```bash
# 1. Authenticate with ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.us-east-1.amazonaws.com

# 2. Build with Lambda Dockerfile (IMPORTANT: use -f Dockerfile, not Dockerfile.standard)
docker build -f Dockerfile -t stage:latest .

# 3. Tag image
docker tag stage:latest 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest

# 4. Push to ECR
docker push 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest
```

## One-Line Command

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.us-east-1.amazonaws.com && docker build -f Dockerfile -t stage:latest . && docker tag stage:latest 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest && docker push 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest
```

## Using the Deployment Scripts

### For Linux/Mac (Bash):
```bash
chmod +x deploy_lambda_to_ecr_stage.sh
./deploy_lambda_to_ecr_stage.sh
```

### For Windows (PowerShell):
```powershell
.\deploy_lambda_to_ecr_stage.ps1
```

## Lambda Configuration After Deployment

After pushing the image, configure your Lambda function:

1. **Image URI:** `474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest`
2. **Handler:** Leave **EMPTY** (container images don't use handler field)
3. **Runtime:** Container image (not Python runtime)
4. **Architecture:** x86_64 or arm64 (depending on your Dockerfile)

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

| Dockerfile | Use Case | CMD | When to Use |
|------------|----------|-----|-------------|
| `Dockerfile` | **Lambda** | `CMD ["app.main.handler"]` | ✅ Use this for Lambda |
| `Dockerfile.standard` | ECS/EC2/Other | `CMD ["uvicorn", "app.main:app", ...]` | ❌ Don't use for Lambda |

## Troubleshooting

### If you still get the error:
1. **Verify you're using the correct Dockerfile:**
   ```bash
   # Check which Dockerfile you're using
   docker build -f Dockerfile -t stage:latest .  # ✅ Correct for Lambda
   # NOT: docker build -f Dockerfile.standard ...  # ❌ Wrong for Lambda
   ```

2. **Check the CMD in your Dockerfile:**
   ```bash
   grep CMD Dockerfile
   # Should show: CMD ["app.main.handler"]
   ```

3. **Verify handler exists:**
   ```bash
   grep "handler = Mangum" app/main.py
   # Should show: handler = Mangum(app)
   ```

4. **Check Lambda function configuration:**
   - Handler field should be **EMPTY**
   - Image URI should point to your ECR image
   - Runtime should be "Container image"

### If Lambda times out:
- Increase timeout in Lambda configuration
- Check CloudWatch logs for errors
- Verify database connections are working

### If you get import errors:
- Check that all dependencies are in `requirements.txt`
- Verify `mangum` is installed (required for FastAPI on Lambda)



