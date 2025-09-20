from fastapi import FastAPI
from app.route import predictroute,scrappingroute,userRoute   # your route files
from apscheduler.schedulers.background import BackgroundScheduler
from app.scrapping.statewise import run_job  # your scraper function
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

import pytz

IST = pytz.timezone("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=IST)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Run once immediately when app starts
#     run_job()

#     # # Schedule daily scraping at 7 AM IST
#     # scheduler.add_job(run_job, "cron", hour=7, minute=0)
#     # scheduler.start()
#     print("🚀 Scheduler started: run_job will run daily at 7:00 AM IST")

#     yield  # application runs here

#     # Shutdown scheduler gracefully
#     # scheduler.shutdown()
#     print("🛑 Scheduler stopped")

# Initialize FastAPI app with lifespan
# lifespan=lifespan
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers from each file
app.include_router(predictroute.router, prefix="/api")
app.include_router(scrappingroute.router, prefix="/api")
app.include_router(userRoute.router, prefix="/api")
