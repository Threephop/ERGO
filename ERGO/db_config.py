# db_config.py
import pyodbc

# ฟังก์ชันเชื่อมต่อฐานข้อมูล
def get_db_connection():
    conn_str = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=tcp:threephop.database.windows.net;"
        "DATABASE=threephop;"
        "Authentication=ActiveDirectoryInteractive;"  # หรือ ActiveDirectoryPassword สำหรับการยืนยันตัวตน
        "UID=threephop.t@live.ku.th;"
    )
    return pyodbc.connect(conn_str)
 