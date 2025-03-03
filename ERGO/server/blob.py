from fastapi import APIRouter, UploadFile, File, HTTPException
from storage_config import get_blob_service_client, get_container_client
import uuid
import os
from db_config import get_db_connection
import pandas as pd
import io

blob_router = APIRouter()

# API เช็คการเชื่อมต่อกับ Blob Storage
@blob_router.get("/check_blob_storage/")
async def check_blob_storage(container_name: str):
    try:
        # เชื่อมต่อกับ Azure Blob Storage และ container ที่ต้องการ
        container_client = get_container_client(container_name)

        # ตรวจสอบว่า container สามารถเข้าถึงได้หรือไม่
        blob_list = container_client.list_blobs()

        # ถ้ามี blob ใน container หรือเชื่อมต่อสำเร็จ จะส่งกลับข้อความ
        blob_names = [blob.name for blob in blob_list]
        return {"message": "Connection successful", "blobs_in_container": blob_names}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to Blob Storage: {e}")

# API สำหรับอัปโหลดไฟล์วิดีโอไปยัง Blob Storage
@blob_router.post("/upload_file/")
async def upload_video(user_id: int, file: UploadFile = File(...), container_name: str = "ergo"):
    # ตรวจสอบว่าไฟล์ถูกส่งมาหรือไม่
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # เชื่อมต่อกับ Azure Blob Storage ผ่านฟังก์ชันที่นำเข้าจาก storage_config
    blob_service_client = get_blob_service_client()
    container_client = get_container_client(container_name)

    # สร้างชื่อไฟล์ใหม่เพื่อป้องกันการซ้ำซ้อน โดยใช้ UUID
    new_filename = str(uuid.uuid4()) + "_" + file.filename
    
    # สร้าง blob client สำหรับอัพโหลดไฟล์
    blob_client = container_client.get_blob_client(new_filename)

    try:
        # อ่านข้อมูลไฟล์จาก UploadFile และอัปโหลดไปยัง Blob Storage โดยตรง
        file_content = await file.read()  # อ่านไฟล์เป็น bytes
        
        # ใช้ io.BytesIO แทนการเขียนไฟล์ลงดิสก์
        blob_client.upload_blob(io.BytesIO(file_content), overwrite=True)  # อัปโหลดไฟล์โดยตรงไปยัง Azure

        # สร้าง URL ของไฟล์ที่อัพโหลด
        file_url = f"https://ergostorageblob.blob.core.windows.net/{container_name}/{new_filename}"

        # ถ้าต้องการบันทึก URL ลงฐานข้อมูล คุณสามารถทำตามนี้ได้
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SET NOCOUNT ON;
            INSERT INTO dbo.CommunityPosts_Table (user_id, video_path)
            OUTPUT INSERTED.post_id
            VALUES (?, ?)
        """

        cursor.execute(query, (user_id, file_url))  # ส่งค่าตามลำดับที่ถูกต้อง
        print(f"type(user_id): {type(user_id)}, type(file_url): {type(file_url)}")

        post_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": "Video uploaded successfully", "video_url": file_url, "user_id": user_id ,"post_id": int(post_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload video: {e}")
    
# API สำหรับอัปโหลดรูปไปยัง Blob Storage
@blob_router.post("/upload_profile/")
async def upload_video(user_id: int, file: UploadFile = File(...), container_name: str = "image-profile"): # เก็บรูปโปรไฟล์ใน container
    # ตรวจสอบว่าไฟล์ถูกส่งมาหรือไม่
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    # เชื่อมต่อกับ Azure Blob Storage ผ่านฟังก์ชันที่นำเข้าจาก storage_config
    blob_service_client = get_blob_service_client()
    container_client = get_container_client(container_name)

    # สร้างชื่อไฟล์ใหม่เพื่อป้องกันการซ้ำซ้อน โดยใช้ UUID
    new_filename = str(uuid.uuid4()) + "_" + file.filename
    
    # สร้าง blob client สำหรับอัพโหลดไฟล์
    blob_client = container_client.get_blob_client(new_filename)

    try:
        # อ่านข้อมูลไฟล์จาก UploadFile และอัปโหลดไปยัง Blob Storage โดยตรง
        file_content = await file.read()  # อ่านไฟล์เป็น bytes
        
        # ใช้ io.BytesIO แทนการเขียนไฟล์ลงดิสก์
        blob_client.upload_blob(io.BytesIO(file_content), overwrite=True)  # อัปโหลดไฟล์โดยตรงไปยัง Azure

        # สร้าง URL ของไฟล์ที่อัพโหลด
        file_url = f"https://ergostorageblob.blob.core.windows.net/{container_name}/{new_filename}"

        # ถ้าต้องการบันทึก URL ลงฐานข้อมูล คุณสามารถทำตามนี้ได้
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dbo.Users_Table WHERE user_id = ?", (user_id,))
        query = """
            UPDATE dbo.Users_Table 
            SET image = ? 
            WHERE user_id = ?
        """
        cursor.execute(query, (file_url, user_id))  # แก้ลำดับพารามิเตอร์ให้ถูกต้อง
        conn.commit()

        return {"message": "image uploaded successfully", "image": file_url, "user_id": user_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload image: {e}")

# ฟังก์ชันดึงข้อมูลโพสต์จากฐานข้อมูล
@blob_router.get("/get_posts/")
def get_posts():
    conn = get_db_connection()
    query = "SELECT * FROM dbo.CommunityPosts_Table"
    df = pd.read_sql(query, conn)
    return df.to_dict(orient="records")
