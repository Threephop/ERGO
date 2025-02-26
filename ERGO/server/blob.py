import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from azure.storage.blob import BlobServiceClient
from storage_config import get_blob_service_client, get_container_client
from db_config import get_db_connection
import pandas as pd

blob_router = APIRouter()

@blob_router.post("/upload_video/")
async def upload_video(file: UploadFile = File(...)):
    # เชื่อมต่อกับ Azure Blob Storage ผ่านฟังก์ชันที่นำเข้าจาก storage_config
    blob_service_client = get_blob_service_client()
    container_name = "ergo"  # หรือสามารถส่ง container_name มาในพารามิเตอร์
    container_client = get_container_client(container_name)

    # สร้างชื่อไฟล์ใหม่เพื่อป้องกันการซ้ำซ้อน โดยใช้ UUID
    new_filename = str(uuid.uuid4()) + "_" + file.filename
    
    # สร้าง blob client สำหรับอัพโหลดไฟล์
    blob_client = container_client.get_blob_client(new_filename)

    try:
        # อัพโหลดไฟล์ไปยัง Blob Storage
        with open(new_filename, "wb") as f:
            f.write(await file.read())
        
        with open(new_filename, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)  # กำหนด overwrite=True เพื่อเขียนทับไฟล์เก่าหากมี

        # สร้าง URL ของไฟล์ที่อัพโหลด
        file_url = f"https://ergostorageblob.blob.core.windows.net/{container_name}/{new_filename}"
        
        # เชื่อมต่อกับฐานข้อมูลและบันทึก URL
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO CommunityPosts_Table (video_path) VALUES (?)"
        cursor.execute(query, (file_url,))
        conn.commit()

        return {"message": "Video uploaded successfully", "video_url": file_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {e}")


# ฟังก์ชันดึงข้อมูลโพสต์จากฐานข้อมูล
@blob_router.get("/get_posts/")
def get_posts():
    conn = get_db_connection()
    query = "SELECT * FROM CommunityPosts_Table"
    df = pd.read_sql(query, conn)
    return df.to_dict(orient="records")
