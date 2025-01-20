from fastapi import FastAPI
from db_config import get_db_connection  # นำเข้า get_db_connection จาก db_config.py

app = FastAPI()

# ฟังก์ชันที่ดึงข้อมูลผู้ใช้งาน
@app.get("/users")
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM dbo.Users_Table")
    users = cursor.fetchall()
    conn.close()
    return {"users": [row[0] for row in users]}

# ฟังก์ชันที่เพิ่มผู้ใช้งาน
@app.post("/add-user")
def add_user(username: str, email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dbo.Users_Table (username, email) VALUES (?, ?)", (username, email))
    conn.commit()
    conn.close()
    return {"message": "User added successfully"}

# ฟังก์ชันที่ดึงรายชื่อตารางทั้งหมดในฐานข้อมูล
@app.get("/tables")
def get_tables():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'")
        tables = cursor.fetchall()
        conn.close()
        return {"tables": [table[0] for table in tables]}
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
