from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import predict  # make sure file exists

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # <-- remove trailing slash
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,                   # optional but recommended
)

# Include router
app.include_router(predict.router, prefix="/api")
