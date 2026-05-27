# ECR Push Commands

## Quick Reference

**Account ID:** 474833638797  
**Repository:** mentee  
**Region:** ap-south-1

## Essential Commands

### 1. Authenticate Docker with ECR
```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com
```

### 2. Build Docker Image
```bash
docker build -t mentee:latest .
```

### 3. Tag Image for ECR
```bash
docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

### 4. Push to ECR
```bash
docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

## One-Liner (All Commands)
```bash
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin 474833638797.dkr.ecr.ap-south-1.amazonaws.com && docker build -t mentee:latest . && docker tag mentee:latest 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest && docker push 474833638797.dkr.ecr.ap-south-1.amazonaws.com/mentee:latest
```

## Using Scripts

### Linux/Mac
```bash
chmod +x ecr_push.sh
./ecr_push.sh
```

### Windows PowerShell
```powershell
.\ecr_push.ps1
```
