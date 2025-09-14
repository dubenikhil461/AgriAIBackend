from fastapi import FastAPI
from app.routes import predict

app = FastAPI()
app.include_router(predict.router, prefix="/api")
