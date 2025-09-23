# from pymongo import MongoClient
# import os
# from dotenv import load_dotenv

# load_dotenv()

# MONGO_URI = os.getenv("MONGO_URI")
# DB_NAME = os.getenv("DB_NAME")

# client = MongoClient(MONGO_URI)
# db = client[DB_NAME]

# app/config/db.py
from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Get Mongo URI and DB name
MONGO_URI = os.getenv("MONGO_URI") or "mongodb://localhost:27017"
DB_NAME = os.getenv("DB_NAME") or "AgriAI_DB"

# Debug print
print("Using MongoDB URI:", MONGO_URI)
print("Using DB Name:", DB_NAME)

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
