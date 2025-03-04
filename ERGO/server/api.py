from fastapi import FastAPI, HTTPException, Form, Request, Query, UploadFile, File
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from datetime import datetime
from db_config import get_db_connection  # นำเข้า get_db_connection จาก db_config.py
import sqlite3
from fastapi import APIRouter
from fastapi.responses import FileResponse
import pyodbc
import pandas as pd
import os


api_router = APIRouter()

# ฟังก์ชันที่ดึงข้อมูลผู้ใช้งาน
@api_router.get("/users")
def get_users():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT user_id, outlook_mail, username, image FROM dbo.Users_Table")
    users = cursor.fetchall()

    conn.close()

    return {"users": [
        {
            "user_id": user[0], 
            "email": user[1], 
            "username": user[2], 
            "profile_url": user[3] if user[3] else None  # ถ้าไม่มี URL ให้เป็น None
        }
        for user in users
    ]}


@api_router.get("/get_user_id/{email}")
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

# 📌 API ค้นหา role จาก email
@api_router.get("/get_user_role/{email}")
def get_user_role(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔹 ดึง role จาก outlook_mail
    cursor.execute("SELECT role FROM dbo.Users_Table WHERE outlook_mail = ?", (email,))
    user = cursor.fetchone()

    conn.close()

    if user:
        return {"email": email, "role": user[0]}  # ส่ง role กลับไป
    return {"error": "User not found"}
    
# ฟังก์ชันที่เพิ่มผู้ใช้งาน
@api_router.post("/add-user")
def add_user(username: str, email: str, role: int, create_at: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ตรวจสอบว่าผู้ใช้มีอยู่แล้วในฐานข้อมูลหรือไม่
    cursor.execute("SELECT username FROM dbo.Users_Table WHERE outlook_mail = ?", (email,))
    existing_user = cursor.fetchone()

    if existing_user:
        # อัปเดตเฉพาะ create_at
        cursor.execute("UPDATE dbo.Users_Table SET create_at = ? WHERE outlook_mail = ?", (create_at, email))
        message = "User login time updated successfully"
    else:
        # ถ้าผู้ใช้งานยังไม่มี ให้ทำการเพิ่มข้อมูลใหม่
        cursor.execute("INSERT INTO dbo.Users_Table (username, outlook_mail, role, create_at) VALUES (?, ?, ?, ?)",
                       (username, email, role, create_at))
        message = "User added successfully"

    conn.commit()
    conn.close()
    return {"message": message}
    
# ฟังก์ชันที่ดึงรายชื่อตารางทั้งหมดในฐานข้อมูล
@api_router.post("/post-message")
def post_message(user_id: int, content: str, create_at: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # ใช้ OUTPUT INSERTED.post_id เพื่อดึงค่า post_id ที่ถูกสร้างขึ้น
        query = """
            INSERT INTO dbo.CommunityPosts_Table (user_id, content, create_at)
            OUTPUT INSERTED.post_id
            VALUES (?, ?, ?)
        """
        cursor.execute(query, (user_id, content, create_at))
        post_id = cursor.fetchone()[0]
        conn.commit()
        return {"message": "Message posted successfully", "post_id": int(post_id)}
    
    except Exception as e:
        conn.rollback()
        return {"error": f"Failed to post message: {str(e)}"}
    
    finally:
        conn.close()



@api_router.get("/get-messages")
def get_messages(user_id: int = Query(None)):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.post_id, c.content, c.create_at, c.user_id, u.username, 
               u.image AS profile_image, c.video_path, 
               COUNT(l.like_id) AS like_count, 
               CASE 
                   WHEN EXISTS (
                       SELECT 1 FROM dbo.Like_Table l2 
                       WHERE l2.post_id = c.post_id AND l2.user_id = ?
                   ) THEN 1 
                   ELSE 0 
               END AS liked_by_user
        FROM dbo.CommunityPosts_Table c
        JOIN dbo.Users_Table u ON c.user_id = u.user_id
        LEFT JOIN dbo.Like_Table l ON c.post_id = l.post_id  
        GROUP BY c.post_id, c.content, c.create_at, c.user_id, u.username, u.image, c.video_path
        ORDER BY c.create_at
    """, (user_id,))

    messages = cursor.fetchall()
    conn.close()

    # ✅ Debug ดูค่าที่ API ส่งกลับ
    print("📌 API Response:")
    for row in messages:
        print(f"🔹 post_id: {row[0]}, profile_image: {row[5]}")

    return {"messages": [
        {
            "post_id": row[0], 
            "content": row[1], 
            "create_at": row[2], 
            "user_id": row[3], 
            "username": row[4], 
            "profile_image": row[5] if row[5] else "https://example.com/default-profile.png",  # ถ้าไม่มี ให้ใช้ Default
            "video_path": row[6], 
            "like_count": row[7],  
            "liked_by_user": row[8]
        }
        for row in messages
    ]}


@api_router.delete("/delete-message/{post_id}")
async def delete_message(post_id: int, request: Request):
    # รับข้อมูล JSON ที่ส่งมาจาก client (คาดว่า {"user_id": <user_id>})
    data = await request.json()
    user_id = data.get("user_id")
    
    # เชื่อมต่อฐานข้อมูล
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # ตรวจสอบว่ามีข้อความที่มี post_id ดังกล่าวหรือไม่
        cursor.execute("SELECT user_id FROM dbo.CommunityPosts_Table WHERE post_id = ?", (post_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Message not found")
        
        # ตรวจสอบว่าข้อความนั้นเป็นของผู้ใช้ที่ร้องขอลบหรือไม่
        if row[0] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized to delete this message")
        
        # ลบข้อความจากฐานข้อมูล
        cursor.execute("DELETE FROM dbo.CommunityPosts_Table WHERE post_id = ?", (post_id,))
        conn.commit()

        return {"message": "Message deleted successfully"}
    
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete message: {str(e)}")
    
    finally:
        conn.close()
        
# API สำหรับการกด Like
@api_router.post("/like")
async def create_like(post_id: int, user_id: int, action: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ตรวจสอบค่า action ว่าเป็น 'like' หรือ 'unlike'
    if action == "like":
        # ตรวจสอบว่า User นี้กด Like ไปแล้วหรือยัง
        cursor.execute("""
            SELECT * FROM dbo.Like_Table
            WHERE post_id = ? AND user_id = ?
        """, (post_id, user_id))
        existing_like = cursor.fetchone()

        if existing_like:
            raise HTTPException(status_code=400, detail="User has already liked this post.")
        
        # เพิ่ม Like ใหม่
        cursor.execute("""
            INSERT INTO dbo.Like_Table (post_id, user_id, create_at)
            VALUES (?, ?, GETDATE())
        """, (post_id, user_id))
        conn.commit()
        message = "Like added successfully."

    elif action == "unlike":
        # ถ้าจะยกเลิก Like
        cursor.execute("""
            DELETE FROM dbo.Like_Table
            WHERE post_id = ? AND user_id = ?
        """, (post_id, user_id))
        conn.commit()
        message = "Like removed successfully."

    else:
        raise HTTPException(status_code=400, detail="Invalid action. Expected 'like' or 'unlike'.")

    # ปิดการเชื่อมต่อฐานข้อมูล
    conn.close()

    return {"message": message}

@api_router.get("/check-like")
def check_like(post_id: int, user_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()

    # ตรวจสอบว่าผู้ใช้ได้กดไลก์โพสต์นี้หรือไม่
    cursor.execute("""
        SELECT COUNT(*) 
        FROM dbo.Like_Table 
        WHERE post_id = ? AND user_id = ?
    """, (post_id, user_id))

    like_count = cursor.fetchone()[0]  # ได้จำนวนที่ตรงกับเงื่อนไข

    # ถ้า count > 0 หมายความว่า user_id ได้ไลก์โพสต์นี้
    is_liked = like_count > 0

    conn.close()

    return {"post_id": post_id, "user_id": user_id, "is_liked": is_liked}

@api_router.get("/get_profile_image")
async def get_profile_image(user_id: int):
    """ API ดึง URL รูปโปรไฟล์ของผู้ใช้จาก Database """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT image FROM dbo.Users_Table WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    row = cursor.fetchone()

    if row and row[0]:  # ถ้ามีค่าในคอลัมน์ image
        return {"profile_url": row[0]}
    
    return {"profile_url": None}  # ถ้าไม่มีรูป

@api_router.get("/get_video_path")
async def get_video_path(post_id: int):
    """ API ดึง URL ของวิดีโอจาก CommunityPosts_Table ตาม post_id """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # ✅ ดึง `video_path` ตาม `post_id`
    query = """
    SELECT video_path 
    FROM dbo.CommunityPosts_Table 
    WHERE post_id = ?
    """
    
    cursor.execute(query, (post_id,))
    row = cursor.fetchone()

    if row and row[0]:  # ถ้ามีวิดีโอในฐานข้อมูล
        return {"video_path": row[0]}
    
    return {"video_path": None}  # ถ้าไม่มีวิดีโอ


@api_router.get("/showstat")
def get_usage_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    # ใช้ LEFT JOIN กับ UsageStats_Table และคำนวณจำนวนไลก์จาก Like_Table
    cursor.execute("""
        SELECT u.user_id, u.username, 
               COALESCE(us.hours_used, 0) AS hours_used, 
               COALESCE(like_counts.like_count, 0) AS like_count
        FROM dbo.Users_Table u
        LEFT JOIN dbo.UsageStats_Table us ON u.user_id = us.user_id
        LEFT JOIN (
            SELECT user_id, COUNT(*) AS like_count
            FROM dbo.Like_Table
            GROUP BY user_id
        ) like_counts ON u.user_id = like_counts.user_id
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
                "like_count": row[3]
            } 
            for row in stats
        ]
    }


# API รับค่าจากแอปและอัปเดต hours_used ใน UsageStats_Table
@api_router.get("/update_app_time/")
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


@api_router.get("/get_usage_stats/{user_id}")
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
            "Monday": row[0] if row[0] is not None else 0,
            "Tuesday": row[1] if row[1] is not None else 0,
            "Wednesday": row[2] if row[2] is not None else 0,
            "Thursday": row[3] if row[3] is not None else 0,
            "Friday": row[4] if row[4] is not None else 0,
            "Saturday": row[5] if row[5] is not None else 0,
            "Sunday": row[6] if row[6] is not None else 0
        }
    else:
        # ถ้าไม่พบข้อมูลใน Dashboard_Table, ให้ทำการ INSERT ข้อมูลใหม่
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

@api_router.get("/get_activity_details/")
def get_activity_details(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔹 ตรวจสอบ role ของ user
    cursor.execute("SELECT role FROM dbo.Users_Table WHERE outlook_mail = ?", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    if user[0] != 1:  # ถ้าไม่ใช่ Admin
        conn.close()
        raise HTTPException(status_code=403, detail="You don't have permission to access this data")

    # 🔹 ดึงข้อมูลจาก Users_Table และ Dashboard_Table
    query = """
    SELECT 
        u.username, 
        d.monday, 
        d.tuesday, 
        d.wednesday, 
        d.thursday, 
        d.friday, 
        d.saturday,
        d.sunday  -- เพิ่มคอมม่าเพื่อแยกคอลัมน์
    FROM dbo.Dashboard_Table d
    JOIN dbo.Users_Table u ON d.user_id = u.user_id
    WHERE u.outlook_mail = ?
    """
    
    cursor.execute(query, (email,))
    data = cursor.fetchone()

    if not data:
        conn.close()
        raise HTTPException(status_code=404, detail="No activity data found for this user")

    # 🔹 เตรียมข้อมูลให้กับ details
    details = [
        data[0],  # Username
        data[1],  # Monday
        data[2],  # Tuesday
        data[3],  # Wednesday
        data[4],  # Thursday
        data[5],  # Friday
        data[6],   # Saturday
        data[7]   # Sunday
    ]

    conn.close()
    
    return {"activity_details": details}


# 🔄 ฟังก์ชันสำหรับอัปเดตชื่อผู้ใช้ (รับค่าเป็น Form Data)
@api_router.post("/update_username/")
def update_username(
    user_id: int = Form(...),  # รับค่า user_id จาก Form Data
    new_username: str = Form(...)  # รับค่า new_username จาก Form Data
):

    if not new_username:
        raise HTTPException(status_code=400, detail="New username cannot be empty")

    conn = get_db_connection()
    cursor = conn.cursor()

    # ตรวจสอบว่ามี user_id ในฐานข้อมูลหรือไม่
    cursor.execute("SELECT * FROM dbo.Users_Table WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    # อัปเดต username
    cursor.execute("UPDATE dbo.Users_Table SET username = ? WHERE user_id = ?", (new_username, user_id))
    conn.commit()
    conn.close()

    return {"message": "Username updated successfully", "user_id": user_id, "new_username": new_username}

def get_unique_filename(directory, filename, extension):
    """ ตรวจสอบชื่อไฟล์ หากมีอยู่แล้วให้เพิ่มเลขต่อท้าย """
    base_name = filename
    counter = 1
    file_path = os.path.join(directory, f"{filename}{extension}")

    while os.path.exists(file_path):
        file_path = os.path.join(directory, f"{base_name} ({counter}){extension}")
        counter += 1

    return file_path

@api_router.get("/export_dashboard_active/")
def export_dashboard(email: str):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔹 ตรวจสอบ role ของ user
    cursor.execute("SELECT role FROM dbo.Users_Table WHERE outlook_mail = ?", (email,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    if user[0] != 1:  # ถ้าไม่ใช่ Admin
        conn.close()
        raise HTTPException(status_code=403, detail="You don't have permission to export data")

    # 🔹 ดึงข้อมูลจาก Users_Table และ Dashboard_Table
    query = """
    SELECT 
        u.username, 
        u.outlook_mail, 
        d.monday, 
        d.tuesday, 
        d.wednesday, 
        d.thursday, 
        d.friday, 
        d.saturday, 
        d.sunday
    FROM dbo.Dashboard_Table d
    JOIN dbo.Users_Table u ON d.user_id = u.user_id
    """
    
    df = pd.read_sql(query, conn)
    conn.close()

    # 🔹 บันทึกไฟล์ไปที่โฟลเดอร์ Downloads ของผู้ใช้ โดยเพิ่มชื่อไฟล์ให้ไม่ซ้ำ
    downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    file_path = get_unique_filename(downloads_folder, "dashboard_active", ".xlsx")
    
    df.to_excel(file_path, index=False)

    # ส่งชื่อไฟล์ที่ได้ไปยัง frontend
    return FileResponse(file_path, filename=os.path.basename(file_path), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@api_router.get("/get_monthly_usage_stats/{user_id}")
def get_monthly_usage_stats(user_id: int):
    """ดึงข้อมูลการใช้งานรายเดือนของผู้ใช้"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 🔹 ตรวจสอบว่ามี user_id ในฐานข้อมูลหรือไม่
    cursor.execute("SELECT * FROM dbo.DashboardMonth_Table WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    conn.close()

    if row:
        return {
            "January": row[2] if row[2] is not None else 0,
            "February": row[3] if row[3] is not None else 0,
            "March": row[4] if row[4] is not None else 0,
            "April": row[5] if row[5] is not None else 0,
            "May": row[6] if row[6] is not None else 0,
            "June": row[7] if row[7] is not None else 0,
            "July": row[8] if row[8] is not None else 0,
            "August": row[9] if row[9] is not None else 0,
            "September": row[10] if row[10] is not None else 0,
            "October": row[11] if row[11] is not None else 0,
            "November": row[12] if row[12] is not None else 0,
            "December": row[13] if row[13] is not None else 0,
        }
    else:
        raise HTTPException(status_code=404, detail="No monthly usage data found for this user")

@api_router.get("/get_profile_url/{user_id}")
def get_profile_url(user_id: int):
    """ ดึง URL รูปโปรไฟล์จากฐานข้อมูล """

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # 🔹 ค้นหา URL รูปโปรไฟล์จาก Users_Table
        cursor.execute("SELECT image FROM dbo.Users_Table WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()

        if row and row[0]:  # ถ้ามีข้อมูล URL
            return {"profile_url": row[0]}
        else:
            raise HTTPException(status_code=404, detail="❌ ไม่พบรูปโปรไฟล์ของผู้ใช้ในฐานข้อมูล")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ เกิดข้อผิดพลาดระหว่างดึงข้อมูล: {e}")

    finally:
        conn.close()  # ปิดการเชื่อมต่อฐานข้อมูล

@api_router.get("/get_user_videos/{user_id}")
def get_user_videos(user_id: int):
    """ ดึงข้อมูลวิดีโอของผู้ใช้จากฐานข้อมูล """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT post_id, video_path AS video_url, image_path AS thumbnail_url, 
           (SELECT COUNT(*) FROM dbo.Like_Table WHERE post_id = c.post_id) AS like_count
    FROM dbo.CommunityPosts_Table c
    WHERE user_id = ?
    """
    cursor.execute(query, (user_id,))
    videos = cursor.fetchall()

    conn.close()

    return {
        "videos": [
            {
                "post_id": row[0],
                "video_url": row[1],
                "thumbnail_url": row[2] if row[2] else None,
                "like_count": row[3]
            }
            for row in videos
        ]
    }


@api_router.get("/refresh_Like/")
def refresh_Like(user_id: int):
    """ รีโหลดข้อมูลโพสต์ของผู้ใช้ทั้งหมด คล้ายกับที่ทำใน Commu """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ เช็คว่ามี user_id นี้อยู่ในระบบหรือไม่
        cursor.execute("SELECT COUNT(*) FROM dbo.Users_Table WHERE user_id = ?", (user_id,))
        user_exists = cursor.fetchone()[0]

        if user_exists == 0:
            return {"message": "User not found", "videos": []}  # 🔹 แจ้งเตือนถ้าไม่พบ user

        # ✅ ดึงวิดีโอของผู้ใช้จากฐานข้อมูล
        query = """
            SELECT c.post_id, c.video_path AS video_url, 
                   COUNT(l.like_id) AS like_count
            FROM dbo.CommunityPosts_Table c
            LEFT JOIN dbo.Like_Table l ON c.post_id = l.post_id  
            WHERE c.user_id = ?
            GROUP BY c.post_id, c.video_path
        """
        
        cursor.execute(query, (user_id,))
        videos = cursor.fetchall()
        conn.close()

        if not videos:
            return {"message": "No videos found", "videos": []}  # 🔹 ป้องกัน `NoneType`

        return {"videos": [{"post_id": row[0], "video_url": row[1], "like_count": row[2]} for row in videos]}
    
    except pyodbc.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@api_router.get("/get_all_profiles/")
def get_all_profiles():
    """ ดึง URL รูปโปรไฟล์ของผู้ใช้ทุกคน """
    conn = get_db_connection()
    cursor = conn.cursor()

    query = "SELECT user_id, image FROM dbo.Users_Table"
    cursor.execute(query)
    profiles = cursor.fetchall()
    conn.close()

    return {
        "profiles": {row[0]: row[1] for row in profiles if row[1]}  # เก็บเฉพาะ user_id กับ image URL
    }

#API ให้ ดึงจำนวนไลก์ทั้งหมดที่โพสต์ของผู้ใช้ได้รับ
@api_router.get("/get_total_likes/{user_id}")
def get_total_likes(user_id: int):
    """ ดึงจำนวนไลก์ทั้งหมดของโพสต์ของผู้ใช้ """
    conn = get_db_connection()
    cursor = conn.cursor()

    # ✅ นับจำนวนไลก์ของโพสต์ทั้งหมดของ user
    cursor.execute("""
        SELECT COUNT(*) 
        FROM dbo.Like_Table 
        WHERE post_id IN (SELECT post_id FROM dbo.CommunityPosts_Table WHERE user_id = ?)
    """, (user_id,))

    like_count = cursor.fetchone()[0]
    conn.close()

    return {"user_id": user_id, "total_likes": like_count}
