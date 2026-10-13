import io 
from PIL import Image
from app.services.image_compressor import compress_image


def test_compress_jpeg_returns_smaller_valid_jpeg(jpeg_bytes: bytes) -> None:
    result = compress_image(jpeg_bytes, quality=70)

    assert result.media_type == 'image/jpeg'
    assert result.original_size == len(jpeg_bytes)
    assert result.compressed_size == len(result.data)
    assert result.compressed_size < result.original_size

    with Image.open(io.BytesIO(result.data)) as out:
        assert out.format == 'JPEG'
        assert out.size == (3840, 2160)
