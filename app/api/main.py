from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import pytz

from app.route import predictroute, scrappingroute, emailroute
from routes.crop_api import router as crop_router
from routes.fertilizer_api import router as fertilizer_router
from app.scrapping.statewise import run_job

IST = pytz.timezone("Asia/Kolkata")
scheduler = BackgroundScheduler(timezone=IST)

async def lifespan(app: FastAPI):
    # run_job()
    scheduler.add_job(run_job, "cron", hour=23, minute=50)
    scheduler.start()
    print("🚀 Scheduler started: run_job will run daily at 11:50pm IST")
    yield
    scheduler.shutdown()
    print("🛑 Scheduler stopped")

app = FastAPI(lifespan=lifespan)

# CORS
origins = [
    "https://agriai-ebon.vercel.app",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root
@app.get("/")
def root():
    return {"message": "API is running"}

# Routers
app.include_router(predictroute.router, prefix="/api")
app.include_router(scrappingroute.router, prefix="/api")
app.include_router(emailroute.router, prefix="/api")
app.include_router(crop_router, prefix="/api")
app.include_router(fertilizer_router, prefix="/api")
