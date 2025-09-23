from fastapi import FastAPI
from app.route import predictroute, scrappingroute, userRoute, emailroute
from apscheduler.schedulers.background import BackgroundScheduler
from app.scrapping.statewise import run_job
from starlette.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
import pytz
import os

IST = pytz.timezone("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=IST)


@asynccontextmanager 
async def lifespan(app: FastAPI):
#  run_job()
  # # Schedule daily scraping at 8 AM IST # 
 scheduler.add_job(run_job, "cron", hour=6, minute=0)
 scheduler.start() 
 print("🚀 Scheduler started: run_job will run daily at 5:00 AM IST")
 yield 
 # Application runs while scheduler is active # # Shutdown scheduler gracefully # 
 scheduler.shutdown() 
 print("🛑 Scheduler stopped")

app = FastAPI(lifespan=lifespan)

# ✅ Allow frontend (both local + deployed)
# origins = [
#     "https://agriai-ebon.vercel.app",  # production frontend
#     "http://localhost:5173",           # local dev
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins="https://agriai-ebon.vercel.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Fix OAuth popup issue (but don’t overrestrict)
class COOPMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response: Response = await call_next(request)
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
        # Only set COEP if you actually need it
        # response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        return response

app.add_middleware(COOPMiddleware)

# Root route
@app.get("/")
def root():
    return {"message": "api is running"}

# Routers
app.include_router(predictroute.router, prefix="/api")
app.include_router(scrappingroute.router, prefix="/api")
app.include_router(userRoute.router, prefix="/api")
app.include_router(emailroute.router, prefix="/api")
