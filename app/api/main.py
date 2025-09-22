from fastapi import FastAPI
from app.route import predictroute, scrappingroute, userRoute, emailroute
from apscheduler.schedulers.background import BackgroundScheduler
from app.scrapping.statewise import run_job
# from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
import pytz

IST = pytz.timezone("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=IST)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     run_job()
#     # Schedule daily scraping at 8 AM IST
#     scheduler.add_job(run_job, "cron", hour=6, minute=0)
#     scheduler.start()
#     print("🚀 Scheduler started: run_job will run daily at 5:00 AM IST")

#     yield  # Application runs while scheduler is active

#     # Shutdown scheduler gracefully
#     scheduler.shutdown()
#     print("🛑 Scheduler stopped")


# Initialize FastAPI app with lifespan
# lifespan=lifespan
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://agriai-ebon.vercel.app"
        # "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
@app.get("/")
def root():
    return {"message": "api is running"}
app.include_router(predictroute.router, prefix="/api")
app.include_router(scrappingroute.router, prefix="/api")
app.include_router(userRoute.router, prefix="/api")
app.include_router(emailroute.router, prefix="/api")
