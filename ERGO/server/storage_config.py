import pyodbc
from azure.storage.blob import BlobServiceClient

def get_blob_service_client():
    # กำหนดข้อมูลสำหรับการเชื่อมต่อกับ Azure Blob Storage
    AZURE_STORAGE_ACCOUNT_NAME = "ergostorageblob"
    AZURE_STORAGE_ACCOUNT_KEY = ""
    # สร้าง client สำหรับเชื่อมต่อกับ Azure Blob Storage
    blob_service_client = BlobServiceClient(
        account_url=f"https://{AZURE_STORAGE_ACCOUNT_NAME}.blob.core.windows.net",
        credential=AZURE_STORAGE_ACCOUNT_KEY
    )
    return blob_service_client

def get_container_client(container_name):
    blob_service_client = get_blob_service_client()
    # รับ container client สำหรับ container ที่ต้องการ
    container_client = blob_service_client.get_container_client(container_name)
    return container_client
