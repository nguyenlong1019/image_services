from dataclasses import dataclass
import io 
from PIL import Image, ImageOps, UnidentifiedImageError


DEFAULT_QUALITY = 70 
MAX_PIXELS = 50_000_000
MIN_QUALITY, MAX_QUALITY = 1, 95 
SUPPORTED_FORMATS = {"JPEG": "image/jpeg", "PNG": "image/png"}


class ImageProcessingError(Exception):
    pass 


class InvalidImageError(ImageProcessingError):
    pass 


class ImageTooLargeError(ImageProcessingError):
    pass 


class UnsupportedFormatError(ImageProcessingError):
    pass 



@dataclass(frozen=True)
class ImageCompressResult:
    data: bytes 
    media_type: str 
    original_size: int 
    compressed_size: int 


def compress_image(
    raw: bytes,
    *,
    quality: int = DEFAULT_QUALITY,
    png_lossy: bool = False
) -> ImageCompressResult:
    img, fmt = _open_and_validate(raw)
    media_type = SUPPORTED_FORMATS[fmt]

    icc_profile = img.info.get("icc_profile")
    img = ImageOps.exif_transpose(img)

    if fmt == 'JPEG':
        data = _encode_jpeg(img, quality, icc_profile)
    else:
        data = _encode_png(img, lossy=png_lossy)
    if len(data) >= len(raw):
        data = raw 
    return ImageCompressResult(
        data=data,
        media_type=media_type,
        original_size=len(raw),
        compressed_size=len(data)
    )


def _open_and_validate(raw: bytes) -> tuple[Image.Image, str]:
    try:
        img = Image.open(io.BytesIO(raw))
    except UnidentifiedImageError as e:
        raise InvalidImageError("The file is not a valid image file") from e 
    except Image.DecompressionBombError as e:
        raise ImageTooLargeError("The image has an excessively high pixel count.") from e
    if img.format not in SUPPORTED_FORMATS:
        raise UnsupportedFormatError(f"Format {img.format} is not supported")
    if img.width * img.height > MAX_PIXELS:
        raise ImageTooLargeError(f"The image exceeds {MAX_PIXELS} pixels")
    try:
        img.load()
    except OSError as e:
        raise InvalidImageError("Corrupted image data") from e
    return img, img.format


def _encode_jpeg(img: Image.Image, quality: int, icc_profile: bytes | None) -> bytes:
    buf = io.BytesIO()
    img.save(
        buf,
        format='JPEG',
        quality=quality,
        optimize=True, # huffman
        progressive=True,
        icc_profile=icc_profile
    )
    return buf.getvalue()


def _encode_png(img: Image.Image, *, lossy: bool) -> bytes:
    if lossy and img.mode in ("RGB", "RGBA"):
        img = img.quantize(colors=256)
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return buf.getvalue()
