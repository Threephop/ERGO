import pyodbc
import os
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

# โหลดค่าจาก .env
load_dotenv()

def get_blob_service_client():
    # โหลดข้อมูลจาก .env
    account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_STORAGE_ACCOUNT_KEY")

    # สร้าง client สำหรับเชื่อมต่อกับ Azure Blob Storage
    blob_service_client = BlobServiceClient(
        account_url=f"https://{account_name}.blob.core.windows.net",
        credential=account_key
    )
    return blob_service_client

def get_container_client(container_name):
    blob_service_client = get_blob_service_client()
    # รับ container client สำหรับ container ที่ต้องการ
    container_client = blob_service_client.get_container_client(container_name)
    return container_client
