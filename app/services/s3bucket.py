import os
import boto3

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# AWS S3 Configuration (set via environment variables)
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "jgi-menteetrackers")
S3_REGION = os.getenv("S3_REGION", "ap-south-1")
S3_EXPIRATION = 600  # 7 days in seconds

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=S3_REGION
)
