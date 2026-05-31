"""Cloudinary upload/storage for documents (PDFs, images, proofs, marksheets)."""
import os
import re
from typing import BinaryIO, Optional, Union

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True,
)

S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "jgi-menteetrackers")
S3_REGION = os.getenv("S3_REGION", "ap-south-1")


def _resource_type_for_key(resource_key: str, content_type: Optional[str] = None) -> str:
    key_lower = resource_key.lower()
    if key_lower.endswith(".pdf") or (content_type and "pdf" in content_type.lower()):
        return "raw"
    if key_lower.endswith((".doc", ".docx", ".xls", ".xlsx", ".zip")):
        return "raw"
    return "auto"


def _public_id_from_key(resource_key: str) -> str:
    """Use logical path as Cloudinary public_id (without file extension)."""
    if "." in resource_key.rsplit("/", 1)[-1]:
        return resource_key.rsplit(".", 1)[0]
    return resource_key


def _legacy_s3_url(resource_key: str) -> str:
    return f"https://{S3_BUCKET_NAME}.s3.{S3_REGION}.amazonaws.com/{resource_key}"


def _parse_cloudinary_url(url: str) -> tuple[Optional[str], Optional[str]]:
    match = re.search(r"/([^/]+)/upload/(?:v\d+/)?(.+)$", url)
    if not match:
        return None, None
    resource_type = match.group(1)
    public_id_with_ext = match.group(2)
    basename = public_id_with_ext.rsplit("/", 1)[-1]
    if "." in basename:
        public_id = public_id_with_ext.rsplit(".", 1)[0]
    else:
        public_id = public_id_with_ext
    return resource_type, public_id


def get_document_url(stored: Optional[str]) -> str:
    """Resolve stored value to a viewable URL (Cloudinary URL, legacy S3 key, or passthrough)."""
    if not stored:
        return ""
    if stored.startswith("http://") or stored.startswith("https://"):
        return stored
    return _legacy_s3_url(stored)


def upload_fileobj(
    file_obj: BinaryIO,
    bucket: Optional[str],
    key: str,
    ExtraArgs: Optional[dict] = None,
) -> str:
    """Upload a file to Cloudinary. Returns secure_url to store in the database."""
    content_type = (ExtraArgs or {}).get("ContentType")
    resource_type = _resource_type_for_key(key, content_type)
    public_id = _public_id_from_key(key)

    result = cloudinary.uploader.upload(
        file_obj,
        public_id=public_id,
        resource_type=resource_type,
        overwrite=True,
    )
    return result["secure_url"]


def upload_bytes(content: bytes, key: str, content_type: Optional[str] = None) -> str:
    import io
    return upload_fileobj(
        io.BytesIO(content),
        None,
        key,
        ExtraArgs={"ContentType": content_type or "application/octet-stream"},
    )


def delete_document(stored: Optional[str]) -> None:
    """Delete from Cloudinary when stored value is a Cloudinary URL."""
    if not stored or not stored.startswith("http"):
        return
    if "cloudinary.com" not in stored:
        return
    resource_type, public_id = _parse_cloudinary_url(stored)
    if not public_id:
        return
    try:
        cloudinary.uploader.destroy(public_id, resource_type=resource_type or "image")
    except Exception as exc:
        print(f"Warning: Cloudinary delete failed for {public_id}: {exc}")


def delete_object(Bucket=None, Key=None) -> None:
    """Backward-compatible delete helper (Key may be URL or legacy path)."""
    delete_document(Key)


def generate_view_url(stored: Optional[str], expires_in: int = 600) -> str:
    """Return view URL (Cloudinary URLs are already public; legacy S3 keys get constructed URL)."""
    return get_document_url(stored)
