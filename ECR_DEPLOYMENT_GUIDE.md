# ECR Deployment Guide

## Configuration
- **AWS Account ID**: 474833638797
- **Repository Name**: mentee
- **Region**: ap-south-1
- **ECR URI**: `474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee`

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

## Manual Deployment Commands

### Step 1: Login to ECR
```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com
```

**PowerShell (Windows):**
```powershell
$password = aws ecr get-login-password --region ap-south-1
$password | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com
```

### Step 2: Build Docker Image
```bash
docker build -t mentee:latest .
```

### Step 3: Tag Image for ECR
```bash
docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

### Step 4: Push Image to ECR
```bash
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

---

## All-in-One Command (Linux/Mac)
```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com && \
docker build -t mentee:latest . && \
docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest && \
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

---

## Verify Deployment

### List Images in ECR
```bash
aws ecr list-images --repository-name mentee --region ap-south-1
```

### Describe Image Tags
```bash
aws ecr describe-images --repository-name mentee --region ap-south-1
```

---

## Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws --version
   aws configure
   ```

2. **Docker installed and running**
   ```bash
   docker --version
   docker ps
   ```

3. **ECR Repository exists** (create if needed)
   ```bash
   aws ecr create-repository --repository-name mentee --region ap-south-1
   ```

---

## Troubleshooting

### If ECR repository doesn't exist:
```bash
aws ecr create-repository --repository-name mentee --region ap-south-1
```

### If login fails:
- Check AWS credentials: `aws sts get-caller-identity`
- Verify region: `aws ecr describe-repositories --region ap-south-1`

### If push fails:
- Check image size (ECR has limits)
- Verify repository permissions
- Check AWS account ID matches

---

## Image URI Reference
```
474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

Use this URI when:
- Configuring Lambda functions
- Setting up ECS tasks
- Referencing the image in other AWS services

