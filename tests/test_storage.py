from unittest.mock import patch, MagicMock
from app.services.storage import StorageService


def test_generate_presigned_urls_count():
    mock_client = MagicMock()
    mock_client.generate_presigned_url.return_value = "https://s3.example.com/upload"
    with patch("app.services.storage._s3_client", return_value=mock_client):
        svc = StorageService.__new__(StorageService)
        svc.bucket = "test-bucket"
        svc.region = "me-central-1"
        svc.endpoint = ""
        results = svc.generate_presigned_urls(3)
    assert len(results) == 3
    assert all("upload_url" in r and "key" in r and "photo_index" in r for r in results)
    assert [r["photo_index"] for r in results] == [0, 1, 2]


def test_public_url_format():
    svc = StorageService.__new__(StorageService)
    svc.bucket = "my-bucket"
    svc.region = "me-central-1"
    svc.endpoint = ""
    url = svc._public_url("items/test.jpg")
    assert url == "https://my-bucket.s3.me-central-1.amazonaws.com/items/test.jpg"


def test_public_url_with_endpoint():
    svc = StorageService.__new__(StorageService)
    svc.bucket = "my-bucket"
    svc.region = "me-central-1"
    svc.endpoint = "https://minio.local"
    url = svc._public_url("items/test.jpg")
    assert url == "https://minio.local/my-bucket/items/test.jpg"
