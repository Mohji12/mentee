# ECR Deployment Commands for Stage Repository

## Configuration
- **AWS Account ID**: 474833638797
- **Repository Name**: stage
- **Region**: us-east-1
- **ECR URI**: `474833638797.dkr.ecr.us-east-1.amazonaws.com/stage`

## Individual Commands

### 1. Authenticate with ECR
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.us-east-1.amazonaws.com
```

### 2. Build Docker Image
```bash
docker build -f Dockerfile.standard -t stage:latest .
```

### 3. Tag Image for ECR
```bash
docker tag stage:latest 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest
```

### 4. Push Image to ECR
```bash
docker push 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest
```

## One-Line Command (All Steps Combined)
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.us-east-1.amazonaws.com && \
docker build -f Dockerfile.standard -t stage:latest . && \
docker tag stage:latest 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest && \
docker push 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest
```

## Using the Deployment Scripts

### For Linux/Mac (Bash):
```bash
chmod +x deploy_to_ecr_stage.sh
./deploy_to_ecr_stage.sh
```

### For Windows (PowerShell):
```powershell
.\deploy_to_ecr_stage.ps1
```

## Prerequisites

1. **AWS CLI installed and configured**
   ```bash
   aws --version
   aws configure
   ```

2. **Docker installed and running**
   ```bash
   docker --version
   ```

3. **ECR Repository created** (if not already created)
   ```bash
   aws ecr create-repository --repository-name stage --region us-east-1
   ```

## Additional Useful Commands

### List images in ECR
```bash
aws ecr list-images --repository-name stage --region us-east-1
```

### Delete an image from ECR
```bash
aws ecr batch-delete-image --repository-name stage --image-ids imageTag=latest --region us-east-1
```

### Pull image from ECR
```bash
docker pull 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest
```

### Run the image locally
```bash
docker run -p 8000:8000 474833638797.dkr.ecr.us-east-1.amazonaws.com/stage:latest
```

## Troubleshooting

### If ECR login fails:
- Ensure AWS credentials are configured: `aws configure list`
- Check IAM permissions for ECR access
- Verify the repository exists: `aws ecr describe-repositories --region us-east-1`

### If Docker build fails:
- Check Dockerfile.standard exists
- Verify all dependencies in requirements.txt are correct
- Check Docker daemon is running: `docker ps`

### If push fails:
- Ensure you're logged in to ECR (run step 1 again)
- Check repository permissions
- Verify image tag matches ECR URI format



