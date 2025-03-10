# db_config.py
# import pyodbc

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
# def get_db_connection():
#     conn_str = (
#         "DRIVER={ODBC Driver 17 for SQL Server};"
#         "SERVER=tcp:threephop.database.windows.net;"
#         "DATABASE=threephop;"
#         "Authentication=ActiveDirectoryInteractive;"  # หรือ ActiveDirectoryPassword สำหรับการยืนยันตัวตน
#         "UID=threephop.t@live.ku.th;"
#     )
#     return pyodbc.connect(conn_str)
 
# db_config.py database in my Notebook
# import pyodbc

# def get_db_connection():
#     conn_str = (
#         "DRIVER={ODBC Driver 17 for SQL Server};"
#         "SERVER=DESKTOP-UF0RM52;"
#         "DATABASE=ERGO;"
#         "Trusted_Connection=yes;"  # ใช้ Windows Authentication (แนะนำสำหรับเครื่อง local)
#     )
#     return pyodbc.connect(conn_str)


# db_config.py database in my computer
# import pyodbc

# def get_db_connection():
#     conn_str = (
#         "DRIVER={ODBC Driver 17 for SQL Server};"
#         "SERVER=THREEPHOP\MSSQLSERVER01;"
#         "DATABASE=ERGO;"
#         "Trusted_Connection=yes;"  # ใช้ Windows Authentication (แนะนำสำหรับเครื่อง local)
#     )
#     return pyodbc.connect(conn_str)

# db_config.py database in ERGOSERVER
# import pyodbc
# from azure.storage.blob import BlobServiceClient

# def get_db_connection():
#     conn_str = (
#         "DRIVER={ODBC Driver 17 for SQL Server};"
#         "SERVER=pocergoserver.database.windows.net;"
#         "DATABASE=POCERGODATABASE;"
#         "Authentication=ActiveDirectoryInteractive;"  # หรือ ActiveDirectoryPassword สำหรับการยืนยันตัวตน
#         "UID=ergoepi@outlook.co.th;"
#     )
#     return pyodbc.connect(conn_str)

# db_config.py database in ERGOSERVER SQL login
import pyodbc
from azure.storage.blob import BlobServiceClient
import os
from dotenv import load_dotenv

# โหลดค่าจาก .env
load_dotenv()

def get_db_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=pocergoserver.database.windows.net;"
        "DATABASE=POCERGODATABASE;"
        f"UID={os.getenv('SQL_UID')};"
        f"PWD={os.getenv('SQL_PWD')};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )
    return pyodbc.connect(conn_str)