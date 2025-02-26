from fastapi import FastAPI
from api import api_router  # นำเข้า router จากไฟล์ api.py
from blob import blob_router  # นำเข้า router จากไฟล์ blob.py
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # หรือกำหนดเฉพาะ domain ที่อนุญาต
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# รวม router ต่าง ๆ จากไฟล์ api.py และ blob.py
app.include_router(api_router)
app.include_router(blob_router)
