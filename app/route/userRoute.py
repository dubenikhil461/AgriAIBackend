from fastapi import APIRouter, Request, HTTPException
from jose import jwt
from google.oauth2 import id_token
from google.auth.transport import requests
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")


@router.post("/auth/google")
async def google_auth(request: Request):
    body = await request.json()
    token = body.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token required")

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    payload = {"email": idinfo["email"],"exp": datetime.utcnow() + timedelta(hours=24)}
    backend_jwt = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"jwt": backend_jwt, "user": idinfo}
