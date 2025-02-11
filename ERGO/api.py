from fastapi import FastAPI, HTTPException
from db_config import get_db_connection  # นำเข้า get_db_connection จาก db_config.py

app = FastAPI()

# ฟังก์ชันที่ดึงข้อมูลผู้ใช้งาน
@app.get("/users")
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ค้นหาผู้ใช้ทั้งหมด
    cursor.execute("SELECT outlook_mail, username FROM dbo.Users_Table")
    users = cursor.fetchall()

    conn.close()

    # สร้าง list ของ dictionary
    users_list = [{"email": user[0], "username": user[1]} for user in users]

    return {"users": users_list}

@app.get("/get_user_id/{email}")
def get_user_id(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 🔹 ค้นหา user_id โดยใช้ email
    cursor.execute("SELECT user_id FROM dbo.Users_Table WHERE outlook_mail = ?", (email,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        return {"user_id": user[0]}  # ส่ง user_id กลับไป
    return {"error": "User not found"}

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
    
# ฟังก์ชันสำหรับส่งข้อความเข้า community
@app.post("/post-message")
def post_message(content: str, create_at: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # เพิ่มข้อความใหม่เข้า database
        cursor.execute(
            "INSERT INTO dbo.CommunityPosts_Table (content, create_at) VALUES (?, ?)",
            (content, create_at)
        )
        conn.commit()
        return {"message": "Message posted successfully"}
    
    except Exception as e:
        conn.rollback()
        return {"error": f"Failed to post message: {str(e)}"}
    
    finally:
        conn.close()

# ฟังก์ชันดึงข้อความทั้งหมดจาก community
@app.get("/get-messages")
def get_messages():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT content, create_at FROM dbo.CommunityPosts_Table ORDER BY create_at")
    messages = cursor.fetchall()
    conn.close()
    return {"messages": [{"content": row[0], "create_at": row[1]} for row in messages]}

@app.get("/showstat")
def get_usage_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ใช้ LEFT JOIN เพื่อดึง user ทั้งหมด แม้ว่าจะไม่มีข้อมูลใน UsageStats_Table
    cursor.execute("""
        SELECT u.user_id, u.username, 
               COALESCE(us.hours_used, 0) AS hours_used, 
               COALESCE(us.kcal_burned, 0) AS kcal_burned, 
               COALESCE(us.like_count_id, 0) AS like_count_id
        FROM dbo.Users_Table u
        LEFT JOIN dbo.UsageStats_Table us ON u.user_id = us.user_id
    """)

    stats = cursor.fetchall()
    conn.close()

    # แปลงข้อมูลเป็น JSON
    return {
        "stats": [
            {
                "user_id": row[0],
                "username": row[1],
                "hours_used": row[2],
                "kcal_burned": row[3],
                "like_count_id": row[4]
            } 
            for row in stats
        ]
    }


# API รับค่าจากแอปและอัปเดต hours_used ใน UsageStats_Table
@app.get("/update_app_time/")
def update_app_time(email: str, app_time: float):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 🔹 ค้นหา user_id จาก Users_Table
    cursor.execute("SELECT user_id FROM dbo.Users_Table WHERE outlook_mail = ?", (email,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user[0]
    
    # 🔹 ดึงค่าปัจจุบันของ hours_used จาก UsageStats_Table
    cursor.execute("SELECT hours_used FROM dbo.UsageStats_Table WHERE user_id = ?", (user_id,))
    current_hours = cursor.fetchone()
    
    if current_hours and current_hours[0] is not None:
        new_hours = float(current_hours[0]) + (app_time / 3600)  # แปลงวินาทีเป็นชั่วโมงแล้วบวกเพิ่ม
    else:
        new_hours = app_time / 3600  # ถ้ายังไม่มีค่า ให้ใช้ค่าใหม่เลย
    
    # 🔹 อัปเดตค่า hours_used ใน UsageStats_Table
    cursor.execute(
        "UPDATE dbo.UsageStats_Table SET hours_used = ? WHERE user_id = ?", 
        (new_hours, user_id)
    )
    
    conn.commit()
    conn.close()
    
    return {"message": "App time updated successfully", "new_hours_used": new_hours}

@app.get("/get_usage_stats/{user_id}")
def get_usage_stats(user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ดึงข้อมูลชั่วโมงที่ใช้งานจาก Dashboard_Table ตาม user_id
    cursor.execute(
        """
        SELECT monday, tuesday, wednesday, thursday, friday, saturday, sunday
        FROM dbo.Dashboard_Table
        WHERE user_id = ?
        """, (user_id,)
    )
    
    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "Monday": row[0],
            "Tuesday": row[1],
            "Wednesday": row[2],
            "Thursday": row[3],
            "Friday": row[4],
            "Saturday": row[5],
            "Sunday": row[6]
        }
    else:
        raise HTTPException(status_code=404, detail="User data not found")
