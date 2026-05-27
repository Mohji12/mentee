# Docker & ECR Deployment Guide

## Configuration
- **AWS Account ID:** 474833638797
- **ECR Repository:** mentee
- **Region:** ap-south-1
- **ECR URI:** `474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee`

---

## Quick Deployment (Using Scripts)

### For Linux/Mac:
```bash
chmod +x deploy_to_ecr_mentee.sh
./deploy_to_ecr_mentee.sh
```

### For Windows (PowerShell):
```powershell
.\deploy_to_ecr_mentee.ps1
```

---

## Manual Step-by-Step Commands

### Step 1: Create ECR Repository (if not exists)
```bash
aws ecr create-repository \
    --repository-name mentee \
    --region ap-south-1 \
    --image-scanning-configuration scanOnPush=true
```

### Step 2: Login to ECR
```bash
aws ecr get-login-password --region ap-south-1 | \
    docker login --username AWS --password-stdin \
    474833638797.dkr.ecr.ap-south-1.amazonaws.com
```

### Step 3: Build Docker Image
```bash
# ⚠️ IMPORTANT: Choose the correct Dockerfile based on your deployment target

# For Lambda deployment (USE THIS FOR LAMBDA)
docker build -f Dockerfile -t mentee:latest .

# For ECS/EC2/Other container services (NOT for Lambda)
docker build -f Dockerfile.standard -t mentee:latest .
```

**Key Difference:**
- `Dockerfile` → Uses `CMD ["app.main.handler"]` for Lambda
- `Dockerfile.standard` → Uses `CMD ["uvicorn", ...]` for regular containers

### Step 4: Tag Image for ECR
```bash
docker tag mentee:latest \
    474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

### Step 5: Push to ECR
```bash
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

---

## All-in-One Command (Linux/Mac)
```bash
# Set variables
export AWS_ACCOUNT_ID=474833638797
export ECR_REPO_NAME=mentee
export AWS_REGION=ap-south-1
export IMAGE_TAG=latest
export ECR_URI=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}

# Login
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_URI}

# Build (using Dockerfile for Lambda - change to Dockerfile.standard for ECS/EC2)
docker build -f Dockerfile -t ${ECR_REPO_NAME}:${IMAGE_TAG} .

# Tag
docker tag ${ECR_REPO_NAME}:${IMAGE_TAG} ${ECR_URI}:${IMAGE_TAG}

# Push
docker push ${ECR_URI}:${IMAGE_TAG}
```

---

## All-in-One Command (Windows PowerShell)
```powershell
# Set variables
$AWS_ACCOUNT_ID = "474833638797"
$ECR_REPO_NAME = "mentee"
$AWS_REGION = "ap-south-1"
$IMAGE_TAG = "latest"
$ECR_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Login
aws ecr get-login-password --region $AWS_REGION | `
    docker login --username AWS --password-stdin $ECR_URI

# Build (using Dockerfile for Lambda - change to Dockerfile.standard for ECS/EC2)
docker build -f Dockerfile -t "${ECR_REPO_NAME}:${IMAGE_TAG}" .

# Tag
docker tag "${ECR_REPO_NAME}:${IMAGE_TAG}" "${ECR_URI}:${IMAGE_TAG}"

# Push
docker push "${ECR_URI}:${IMAGE_TAG}"
```

---

## Using Different Tags (Versioning)

### Tag with version number:
```bash
# Build and tag with version (using Dockerfile for Lambda)
docker build -f Dockerfile -t mentee:v1.0.0 .
docker tag mentee:v1.0.0 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:v1.0.0
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:v1.0.0
```

### Tag with timestamp:
```bash
TIMESTAMP=$(date +%Y%m%d%H%M%S)
docker build -f Dockerfile -t mentee:${TIMESTAMP} .
docker tag mentee:${TIMESTAMP} 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:${TIMESTAMP}
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:${TIMESTAMP}
```

---

## Verify Deployment

### List images in ECR:
```bash
aws ecr list-images \
    --repository-name mentee \
    --region ap-south-1
```

### Describe repository:
```bash
aws ecr describe-repositories \
    --repository-names mentee \
    --region ap-south-1
```

### Get image details:
```bash
aws ecr describe-images \
    --repository-name mentee \
    --region ap-south-1 \
    --image-ids imageTag=latest
```

---

## Troubleshooting

### Issue 1: "Repository does not exist"
**Solution:** Create the repository first:
```bash
aws ecr create-repository --repository-name mentee --region ap-south-1
```

### Issue 2: "Access Denied"
**Solution:** Ensure your AWS credentials have ECR permissions:
```bash
aws configure list
```

Required IAM permissions:
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:GetDownloadUrlForLayer`
- `ecr:BatchGetImage`
- `ecr:PutImage`
- `ecr:InitiateLayerUpload`
- `ecr:UploadLayerPart`
- `ecr:CompleteLayerUpload`

### Issue 3: "Docker build fails"
**Solution:** Check Dockerfile path and ensure you're in the correct directory:
```bash
ls -la Dockerfile*
# For Lambda:
docker build -f Dockerfile -t mentee:latest .
# For ECS/EC2:
docker build -f Dockerfile.standard -t mentee:latest .
```

### Issue 4: "Runtime.InvalidEntrypoint - uvicorn not found" (Lambda)
**Solution:** You're using the wrong Dockerfile. For Lambda, use `Dockerfile` (not `Dockerfile.standard`):
```bash
# Correct for Lambda:
docker build -f Dockerfile -t mentee:latest .
```

### Issue 5: "Login token expired"
**Solution:** Re-run the login command (tokens expire after 12 hours)

---

## Image URI Format
After successful push, your image URI will be:
```
474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

Use this URI when:
- Deploying to ECS
- Deploying to Lambda
- Deploying to EKS
- Any AWS service that needs the container image

