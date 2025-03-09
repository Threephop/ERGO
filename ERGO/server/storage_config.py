from azure.storage.blob import BlobServiceClient
from azure.identity import AzureCliCredential  # ใช้ AzureCliCredential
from azure.keyvault.secrets import SecretClient

# ตั้งค่าชื่อ Key Vault ของคุณ
KEY_VAULT_URL = "https://ergoconfig.vault.azure.net"  # ใช้ URL ของ Key Vault ที่แท้จริง
SECRET_NAME = "ergostorageblob"  # ชื่อของ Secret ที่เก็บ Azure Storage Account Key

# ฟังก์ชันในการดึงค่า Secret จาก Key Vault โดยใช้ชื่อ Secret
def get_secret():
    # ใช้ AzureCliCredential เพื่อเชื่อมต่อ
    credential = AzureCliCredential()  # ใช้ Azure CLI เป็นการยืนยันตัวตน
    secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
    
    # ดึง Secret โดยใช้ชื่อ Secret
    retrieved_secret = secret_client.get_secret(SECRET_NAME)
    
    return retrieved_secret.value

def get_blob_service_client():
    # ดึงค่า Storage Account Key จาก Key Vault
    AZURE_STORAGE_ACCOUNT_KEY = get_secret()  # ดึง Secret ที่เก็บ Azure Storage Account Key

    AZURE_STORAGE_ACCOUNT_NAME = "ergostorageblob"
    print(f"🗄 Storage Key: {AZURE_STORAGE_ACCOUNT_KEY}")  # พิมพ์ค่า Storage Account Key ที่ได้มา
    
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
