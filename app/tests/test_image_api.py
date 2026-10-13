from fastapi.testclient import TestClient
from app.main import app 


client = TestClient(app)


def test_compress_endpoint_returns_compressed_jpeg(jpeg_bytes: bytes):
    response = client.post(
        '/api/v1/image/compress',
        files = {"file": ("photo.jpg", jpeg_bytes, 'image/jpeg')},
        data={'quality': 70}
    )
    assert response.status_code == 200 
    assert response.headers['content-type'] == 'image/jpeg'
    assert int(response.headers['x-original-size']) == len(jpeg_bytes)
    assert int(response.headers['x-compressed-size']) == len(response.content)

    assert len(response.content) < len(jpeg_bytes)
