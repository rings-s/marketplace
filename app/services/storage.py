import uuid
import boto3
from botocore.exceptions import ClientError
from app.config import settings


def _s3_client():
    kwargs = {
        "region_name": settings.S3_REGION,
        "aws_access_key_id": settings.S3_ACCESS_KEY or None,
        "aws_secret_access_key": settings.S3_SECRET_KEY or None,
    }
    if settings.S3_ENDPOINT_URL:
        kwargs["endpoint_url"] = settings.S3_ENDPOINT_URL
    return boto3.client("s3", **kwargs)


class StorageService:
    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.region = settings.S3_REGION
        self.endpoint = settings.S3_ENDPOINT_URL

    def _public_url(self, key: str) -> str:
        if self.endpoint:
            return f"{self.endpoint}/{self.bucket}/{key}"
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

    def generate_presigned_urls(
        self, count: int, item_id: str | None = None, ttl: int = 600
    ) -> list[dict]:
        """Generate batch of presigned PUT URLs for direct S3 upload."""
        client = _s3_client()
        results = []
        prefix = f"items/{item_id}/" if item_id else "items/uploads/"
        for i in range(count):
            key = f"{prefix}{uuid.uuid4()}.jpg"
            url = client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": key,
                    "ContentType": "image/jpeg",
                },
                ExpiresIn=ttl,
            )
            results.append({"upload_url": url, "key": key, "photo_index": i})
        return results

    def confirm_uploads(self, keys: list[str]) -> list[dict]:
        """Verify keys exist in S3 and return their public URLs."""
        client = _s3_client()
        results = []
        for key in keys:
            try:
                client.head_object(Bucket=self.bucket, Key=key)
                results.append({"key": key, "url": self._public_url(key)})
            except ClientError:
                raise ValueError(f"Key not found in storage: {key}")
        return results
