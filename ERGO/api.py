from fastapi import FastAPI, HTTPException
from datetime import datetime
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
def post_message(user_id: int, content: str, create_at: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # บันทึกเฉพาะ user_id และ content
        cursor.execute(
            "INSERT INTO dbo.CommunityPosts_Table (user_id, content, create_at) VALUES (?, ?, ?)",
            (user_id, content, create_at)
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

    # ปรับปรุงคำสั่ง SQL เพื่อดึงข้อมูลจากทั้ง CommunityPosts_Table และ Users_Table
    cursor.execute("""
        SELECT c.content, c.create_at, u.username
        FROM dbo.CommunityPosts_Table c
        JOIN dbo.Users_Table u ON c.user_id = u.user_id
        ORDER BY c.create_at
    """)

    messages = cursor.fetchall()
    conn.close()

    # ส่งข้อมูลที่มีทั้ง content, create_at และ username
    return {"messages": [{"content": row[0], "create_at": row[1], "username": row[2]} for row in messages]}


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

    # 🔹 ดึงชื่อวันปัจจุบัน
    today_day = datetime.today().strftime('%A').lower()  # เช่น 'monday', 'tuesday', ...

    # 🔹 ดึงค่าปัจจุบันของ hours_used จาก UsageStats_Table
    cursor.execute("SELECT hours_used FROM dbo.UsageStats_Table WHERE user_id = ?", (user_id,))
    current_hours = cursor.fetchone()
    
    if current_hours and current_hours[0] is not None:
        new_hours = float(current_hours[0]) + (app_time / 3600)  # แปลงวินาทีเป็นชั่วโมงแล้วบวกเพิ่ม
    else:
        new_hours = app_time / 3600  # ถ้ายังไม่มีค่า ให้ใช้ค่าใหม่เลย
        # 🔹 ถ้าไม่มีข้อมูล ให้ทำการ insert ข้อมูลใหม่ลงใน UsageStats_Table
        cursor.execute(
            "INSERT INTO dbo.UsageStats_Table (user_id, hours_used) VALUES (?, ?)",
            (user_id, new_hours)
        )
    
    # 🔹 อัปเดตค่า hours_used ใน UsageStats_Table
    cursor.execute(
        "UPDATE dbo.UsageStats_Table SET hours_used = ? WHERE user_id = ?", 
        (new_hours, user_id)
    )

    # 🔹 ตรวจสอบว่ามีข้อมูลใน Dashboard_Table ของวันนั้นหรือไม่
    cursor.execute(
        f"SELECT {today_day} FROM dbo.Dashboard_Table WHERE user_id = ?", 
        (user_id,)
    )
    dashboard_hours = cursor.fetchone()

    if dashboard_hours and dashboard_hours[0] is not None:
        # 🔹 ถ้ามี ให้บวกเพิ่ม
        updated_dashboard_hours = float(dashboard_hours[0]) + (app_time / 3600)
        cursor.execute(
            f"UPDATE dbo.Dashboard_Table SET {today_day} = ? WHERE user_id = ?",
            (updated_dashboard_hours, user_id)
        )
    else:
        # 🔹 ถ้ายังไม่มี ให้เพิ่มข้อมูลใหม่
        cursor.execute(
            f"UPDATE dbo.Dashboard_Table SET {today_day} = ? WHERE user_id = ?",
            (app_time / 3600, user_id)
        )
        # 🔹 ถ้าไม่มีข้อมูลใน Dashboard_Table สำหรับ user_id นี้ ให้ insert ข้อมูลใหม่
        cursor.execute(
            f"INSERT INTO dbo.Dashboard_Table (user_id, {today_day}) VALUES (?, ?)",
            (user_id, app_time / 3600)
        )
    
    conn.commit()
    conn.close()
    
    return {
        "message": "App time updated successfully",
        "new_hours_used": new_hours
    }


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

    if row:
        conn.close()
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
        # ถ้าไม่พบข้อมูลใน Dashboard_Table, ให้ทำการ INSERT ข้อมูลใหม่
        # ดึงชื่อวันปัจจุบัน
        today_day = datetime.today().strftime('%A').lower()  # เช่น 'monday', 'tuesday', ...
        
        # ในกรณีที่ไม่มีข้อมูลใน Dashboard_Table ให้เพิ่มข้อมูลเริ่มต้นเป็น 0
        cursor.execute(
            """
            INSERT INTO dbo.Dashboard_Table (user_id, monday, tuesday, wednesday, thursday, friday, saturday, sunday)
            VALUES (?, 0, 0, 0, 0, 0, 0, 0)
            """, (user_id,)
        )
        conn.commit()

        # หลังจาก insert ข้อมูล, ดึงข้อมูลมาแสดง
        cursor.execute(
            """
            SELECT monday, tuesday, wednesday, thursday, friday, saturday, sunday
            FROM dbo.Dashboard_Table
            WHERE user_id = ?
            """, (user_id,)
        )
        row = cursor.fetchone()
        conn.close()
        
        return {
            "Monday": row[0],
            "Tuesday": row[1],
            "Wednesday": row[2],
            "Thursday": row[3],
            "Friday": row[4],
            "Saturday": row[5],
            "Sunday": row[6]
        }

