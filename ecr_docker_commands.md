# ECR and Docker Commands for Mentee Tracker

## Configuration
- **AWS Account ID**: 474833638797
- **ECR Repository**: mentee
- **Region**: ap-south-1
- **ECR URI**: `474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee`

---

## Prerequisites

### 1. Install AWS CLI
```bash
# Verify AWS CLI is installed
aws --version

# Configure AWS credentials (if not already done)
aws configure
```

### 2. Install Docker
```bash
# Verify Docker is installed
docker --version
```

### 3. IAM Permissions Required
Ensure your AWS user/role has:
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`
- `ecr:GetDownloadUrlForLayer`
- `ecr:BatchGetImage`
- `ecr:PutImage`
- `ecr:InitiateLayerUpload`
- `ecr:UploadLayerPart`
- `ecr:CompleteLayerUpload`

Or attach the policy: `AmazonEC2ContainerRegistryFullAccess`

---

## ECR Commands

### 1. Login to ECR

#### For Windows PowerShell:
```powershell
# Get ECR password and login
$password = aws ecr get-login-password --region ap-south-1
$password | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com
```

#### For Windows CMD:
```cmd
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com
```

#### For Linux/Mac:
```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com
```

---

## Docker Commands

### 2. Build Docker Image
```bash
# Build the image
docker build -t mentee:latest .

# Or with a specific Dockerfile
docker build -f Dockerfile -t mentee:latest .
```

### 3. Tag Image for ECR
```bash
# Tag the image with ECR URI
docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest

# Or tag with a specific version
docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:v1.0.0
```

### 4. Push Image to ECR
```bash
# Push latest tag
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest

# Push version tag
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:v1.0.0
```

---

## Complete Deployment Workflow

### One-Line Commands (After initial setup)

#### Windows PowerShell:
```powershell
# Login, Build, Tag, and Push
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com; docker build -t mentee:latest .; docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest; docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

#### Linux/Mac:
```bash
# Login, Build, Tag, and Push
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com && docker build -t mentee:latest . && docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest && docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

---

## Useful ECR Management Commands

### List Images in Repository
```bash
aws ecr list-images --repository-name mentee --region ap-south-1
```

### Describe Repository
```bash
aws ecr describe-repositories --repository-names mentee --region ap-south-1
```

### Delete Image
```bash
# Delete a specific image tag
aws ecr batch-delete-image --repository-name mentee --image-ids imageTag=latest --region ap-south-1

# Delete multiple tags
aws ecr batch-delete-image --repository-name mentee --image-ids imageTag=latest imageTag=v1.0.0 --region ap-south-1
```

### Get Image Details
```bash
aws ecr describe-images --repository-name mentee --region ap-south-1
```

### Create Repository (if doesn't exist)
```bash
aws ecr create-repository --repository-name mentee --region ap-south-1
```

---

## Docker Image Management

### List Local Images
```bash
docker images
```

### Remove Local Image
```bash
docker rmi mentee:latest
docker rmi 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

### Run Image Locally (for testing)
```bash
docker run -p 8000:8000 mentee:latest
```

### View Running Containers
```bash
docker ps
```

### Stop Container
```bash
docker stop <container_id>
```

---

## Troubleshooting

### If login fails:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify region
aws configure get region

# Check ECR repository exists
aws ecr describe-repositories --repository-names mentee --region ap-south-1
```

### If push fails:
```bash
# Verify you're logged in
docker info | grep Username

# Check image exists locally
docker images | grep mentee

# Verify tag is correct
docker images | grep 474833638797.dkr.ecr
```

### Clear Docker cache (if build issues):
```bash
docker system prune -a
```

---

## Quick Reference

```bash
# ECR URI
474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee

# Full workflow (copy-paste ready)
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com
docker build -t mentee:latest .
docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

