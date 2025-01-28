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
def add_user(username: str, email: str, create_at: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ตรวจสอบว่าผู้ใช้มีอยู่แล้วในฐานข้อมูลหรือไม่
    cursor.execute("SELECT COUNT(*) FROM dbo.Users_Table WHERE outlook_mail = ?", (email,))
    existing_user = cursor.fetchone()[0]

    if existing_user > 0:
        # ถ้าผู้ใช้งานมีอยู่แล้ว ให้ทำการอัปเดตชื่อและเวลาล่าสุดแทน
        cursor.execute("UPDATE dbo.Users_Table SET username = ?, create_at = ? WHERE outlook_mail = ?",
                       (username, create_at, email))
        message = "User data updated successfully"
    else:
        # ถ้าผู้ใช้งานยังไม่มี ให้ทำการเพิ่มข้อมูลใหม่
        cursor.execute("INSERT INTO dbo.Users_Table (username, outlook_mail, create_at) VALUES (?, ?, ?)",
                       (username, email, create_at))
        message = "User added successfully"

    conn.commit()
    conn.close()
    return {"message": message}


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
