"""
Document storage facade — uploads go to Cloudinary (replaces S3 for user documents).
"""
from app.services.cloudinary_service import (
    S3_BUCKET_NAME,
    delete_document,
    delete_object,
    generate_view_url,
    get_document_url,
    upload_bytes,
    upload_fileobj,
)

S3_EXPIRATION = 600


class _StorageClient:
    """Minimal compat wrapper for routes that still call s3_client methods."""

    class meta:
        region_name = "ap-south-1"

    def upload_fileobj(self, file_obj, bucket, key, ExtraArgs=None):
        return upload_fileobj(file_obj, bucket, key, ExtraArgs)

    def delete_object(self, Bucket=None, Key=None):
        delete_object(Bucket=Bucket, Key=Key)

    def generate_presigned_url(self, ClientMethod, Params=None, ExpiresIn=None):
        key = (Params or {}).get("Key", "")
        return generate_view_url(key, ExpiresIn or S3_EXPIRATION)


s3_client = _StorageClient()
