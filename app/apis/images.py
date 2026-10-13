from typing import Annotated 
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import Response 
from app.services.image_compressor import (
    ImageTooLargeError,
    InvalidImageError,
    UnsupportedFormatError,
    compress_image
)


router = APIRouter(prefix='/api/v1/image', tags=['image'])

EXTENSIONS = {'image/jpeg': 'jpg', 'image/png': 'png'}
MAX_FILE_SIZE_PER_IMAGE = 20_971_520
CHUNK_SIZE = 1_048_576


async def _read_with_limit(file: UploadFile, limit: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while chunk := await file.read(CHUNK_SIZE):
        total += len(chunk)
        if total > limit:
            raise HTTPException(status_code=413, detail='Content too large')
        chunks.append(chunk)
    return b"".join(chunks)


@router.post(
    "/compress"
)
async def compress_image_api(
    file: Annotated[UploadFile, File()],
    quality: Annotated[int, Form(ge=1, le=95)] = 70,
    png_lossy: Annotated[bool, Form()] = False
) -> Response:
    raw = await _read_with_limit(file, MAX_FILE_SIZE_PER_IMAGE)
    if not raw:
        raise HTTPException(status_code=400, detail='File empty')
    try:
        result = await run_in_threadpool(
            compress_image,
            raw,
            quality=quality,
            png_lossy=png_lossy
        )
    except UnsupportedFormatError as e:
        raise HTTPException(status_code=415, detail=str(e)) from e 
    except (InvalidImageError, ImageTooLargeError) as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    ext = EXTENSIONS[result.media_type]
    return Response(
        content=result.data,
        media_type=result.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="compressed.{ext}"',
            "X-Original-Size": str(result.original_size),
            "X-Compressed-Size": str(result.compressed_size),
        }
    )
