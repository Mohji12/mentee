# AWS ECR Configuration
$AWS_ACCOUNT_ID = "474833638797"
$ECR_REPO_NAME = "mentee"
$AWS_REGION = "ap-south-1"
$IMAGE_TAG = "latest"

# ECR Repository URL
$ECR_REPO_URI = "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}"

# Step 1: Authenticate Docker with ECR
$loginCommand = (aws ecr get-login-password --region $AWS_REGION) | docker login --username AWS --password-stdin $ECR_REPO_URI

# Step 2: Build Docker image
docker build -t "${ECR_REPO_NAME}:${IMAGE_TAG}" .

# Step 3: Tag the image for ECR
docker tag "${ECR_REPO_NAME}:${IMAGE_TAG}" "${ECR_REPO_URI}:${IMAGE_TAG}"

# Step 4: Push to ECR
docker push "${ECR_REPO_URI}:${IMAGE_TAG}"

Write-Host "Image pushed successfully to ${ECR_REPO_URI}:${IMAGE_TAG}"


