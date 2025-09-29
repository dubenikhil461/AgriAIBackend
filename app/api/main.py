from fastapi import FastAPI
from app.route import predictroute, scrappingroute, userRoute, emailroute
from apscheduler.schedulers.background import BackgroundScheduler
# from app.scrapping.statewise import run_job
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import pytz
import os

# ✅ Import your new APIs
from routes.crop_api import router as crop_router
from routes.fertilizer_api import router as fertilizer_router

IST = pytz.timezone("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=IST)

# @asynccontextmanager 
# async def lifespan(app: FastAPI):
#     run_job()
#     scheduler.add_job(run_job, "cron", hour=23, minute=50)
#     scheduler.start() 
#     print("🚀 Scheduler started: run_job will run daily at 11:50pm :00 AM IST")
#     yield 
#     scheduler.shutdown() 
#     print("🛑 Scheduler stopped")

# app = FastAPI(lifespan=lifespan)
app = FastAPI()

# ✅ Allow frontend (both local + deployed)
origins = [
    "https://agriai-ebon.vercel.app",  # production frontend
    "http://localhost:5173",           # local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RemoveCOOPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        if "cross-origin-opener-policy" in response.headers:
            del response.headers["cross-origin-opener-policy"]
        if "cross-origin-embedder-policy" in response.headers:
            del response.headers["cross-origin-embedder-policy"]
        return response

app.add_middleware(RemoveCOOPMiddleware)

# Root route
@app.get("/")
def root():
    return {"message": "api is running"}

# Routers
app.include_router(predictroute.router, prefix="/api")
app.include_router(scrappingroute.router, prefix="/api")
app.include_router(userRoute.router, prefix="/api")
app.include_router(emailroute.router, prefix="/api")

# ✅ Add Crop & Fertilizer APIs
app.include_router(crop_router, prefix="/api")
app.include_router(fertilizer_router, prefix="/api")
