from fastapi import FastAPI, Header, HTTPException, Depends 
from api import api_router
from blob import blob_router
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi import Request
from dotenv import load_dotenv  # ✅ โหลดค่า .env

load_dotenv()  # ✅ โหลดค่า .env

api_key = os.getenv("api_key")  # ✅ ตรวจสอบ API Key

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ฟังก์ชันตรวจสอบ API Key
def verify_api_key(request: Request, x_api_key: str = Header(None)):
    query_api_key = request.query_params.get("x_api_key")
    if x_api_key != api_key and query_api_key != api_key:
        raise HTTPException(status_code=403, detail="Forbidden: Invalid API Key")

# รวม router และใช้ verify_api_key เป็น Dependency
app.include_router(api_router, dependencies=[Depends(verify_api_key)])
app.include_router(blob_router, dependencies=[Depends(verify_api_key)])
