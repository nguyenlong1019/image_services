from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from app.apis.images import router as images_router


app = FastAPI()
app.include_router(images_router)


app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
