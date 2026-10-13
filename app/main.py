from fastapi import FastAPI
from app.apis.images import router as images_router


app = FastAPI()
app.include_router(images_router)
