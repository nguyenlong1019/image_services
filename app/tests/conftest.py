import io 
import pytest
from PIL import Image


@pytest.fixture
def jpeg_bytes() -> bytes:
    img = Image.effect_noise((3840, 2160), 64).convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=95)
    return buf.getvalue()


# python -m pytest -v
