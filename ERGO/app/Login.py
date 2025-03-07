import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from msal import PublicClientApplication
from profile_frame import ProfileFrame
from main import App
import win32gui
import win32con
import webbrowser
import os
import requests
import datetime
import subprocess

# Microsoft App Configuration
CLIENT_ID = "e05e1663-bc57-4c87-ab60-d41463b12dcb"
AUTHORITY = "https://login.microsoftonline.com/8c1832ea-a96d-413e-bf7d-9fe4d608e00b"
REDIRECT_URI = "http://localhost:3000"
SCOPES = ["User.Read"]
icon_dir = os.path.join(os.path.dirname(__file__), "icon")
file_dir = os.path.join(os.path.dirname(__file__))
mainPY = os.path.join(file_dir, "main.py")
icon_path = os.path.join(icon_dir, "windows_icon.ico")

def change_taskbar_icon(window, icon_path):
    try:
        window.iconbitmap(icon_path)  # Set icon for window and taskbar
    except Exception as e:
        print(f"Error changing icon: {e}")


# API endpoint for adding user data to the database
API_ENDPOINT = "http://localhost:8000/add-user"

# Function to send username and email to API
def send_user_data(username, email, created_at):
    try:
        payload = {"username": username, "email": email, "create_at": created_at}
        response = requests.post(API_ENDPOINT, params=payload)
        if response.status_code == 200:
            messagebox.showinfo("Success", "User data sent successfully.")
        else:
            messagebox.showerror("Error", f"Failed to send data: {response.text}")
    except Exception as e:
        messagebox.showerror("Error", f"Error communicating with API: {e}")

def get_user_id_from_db(email):
    url = f"http://127.0.0.1:8000/get_user_id/{email}"  # เรียก API ที่เขียนใน FastAPI
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data.get("user_id")
    
    return None  # ถ้าไม่เจอ user_id

# ฟังก์ชัน Log in
def login():
    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    try:
        auth_result = app.acquire_token_interactive(scopes=SCOPES)
        if "access_token" in auth_result:
            access_token = auth_result["access_token"]
            headers = {"Authorization": f"Bearer {access_token}"}
            graph_endpoint = "https://graph.microsoft.com/v1.0/me"

            response = requests.get(graph_endpoint, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                email = user_data.get("mail") or user_data.get("userPrincipalName")  # ดึงอีเมลที่ใช้ล็อกอิน
                username = user_data.get("displayName")

                if email and username:
                    created_at = datetime.datetime.utcnow().isoformat()
                    role = 0 # 0 = User, 1 = Admin

                    # 🔹 เรียก API `/add-user` เพื่อเพิ่มผู้ใช้ก่อน
                    add_user_response = requests.post(
                        "http://127.0.0.1:8000/add-user",
                        params={"username": username, "email": email, "role": role, "create_at": created_at}
                    )

                    if add_user_response.status_code == 200:
                        print("✅ User added successfully!")

                        # 🔹 ค้นหา user_id หลังจากเพิ่มข้อมูล
                        user_id = get_user_id_from_db(email)  

                        if user_id:
                            messagebox.showinfo("Login Success", f"Welcome {username}! Email: {email}")

                            # ✅ ส่ง email ไป main.py แทน user_id
                            root.destroy()  # ปิดหน้าต่าง Login
                            # เปิดหน้าต่าง Main โดยส่งค่า email ไป
                            main_app = App(email)  # เรียกคลาส App จาก main.py
                            main_app.mainloop()
                        else:
                            messagebox.showerror("Error", "User ID not found in the database after adding.")
                    else:
                        messagebox.showerror("Error", "Failed to add user.")
                else:
                    messagebox.showerror("Error", "User data is incomplete.")
            else:
                messagebox.showerror("Error", "Failed to retrieve user info.")
        else:
            messagebox.showerror("Login Failed", "Unable to authenticate.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

# ฟังก์ชัน Sign Up
def signup():
    webbrowser.open("https://signup.live.com/")

# ฟังก์ชัน Guest
def guest():
    messagebox.showinfo("Guest", "Guest clicked!")

# ฟังก์ชัน Logout
def logout():
    try:
        logout_url = "https://login.microsoftonline.com/common/oauth2/v2.0/logout"
        webbrowser.open(logout_url)  # เปิดหน้าต่างเบราว์เซอร์เพื่อทำการ logout

        # แจ้งเตือนผู้ใช้ว่าทำการ Logout สำเร็จ
        messagebox.showinfo("Logout", "You have been logged out. Restarting login flow.")

        # เรียกฟังก์ชัน login เพื่อเปิดหน้าต่างการเข้าสู่ระบบใหม่
        # login()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during logout: {e}")

# สร้างหน้าต่างหลัก
root = tk.Tk()
# เปลี่ยนไอคอนใน Taskbar
change_taskbar_icon(root, icon_path)
root.title("ERGO PROJECT")
root.iconbitmap(os.path.join(icon_dir, "GODJI-Action_200113_0008.ico"))
# ขนาดหน้าต่าง
window_width = 1024
window_height = 768

# คำนวณตำแหน่งเพื่อให้หน้าต่างอยู่ตรงกลางจอ
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x_cordinate = int((screen_width / 2) - (window_width / 2))
y_cordinate = int((screen_height / 2) - (window_height / 2))

# ตั้งค่าตำแหน่งหน้าต่าง
root.geometry(f"{window_width}x{window_height}+{x_cordinate}+{y_cordinate}")
root.configure(bg="black")

# ส่วนซ้าย (สีพื้นหลังน้ำเงิน)
left_frame = tk.Frame(root, bg="#1B1464", width=300, height=400)
left_frame.pack(side="left", fill="y")

# ใส่ GODJI (ปรับให้แสดงรูปภาพ)
try:
    or_logo_path = os.path.join(icon_dir, "GODJI Action_200113_0008.png")  # Path ของภาพ
    or_logo_image = Image.open(or_logo_path)  # เปิดไฟล์ภาพ
    or_logo_image = or_logo_image.resize((150, 150), Image.Resampling.LANCZOS)  # ปรับขนาด
    or_logo_photo = ImageTk.PhotoImage(or_logo_image)  # แปลงเป็น PhotoImage
    or_logo_label = tk.Label(left_frame, image=or_logo_photo, bg="#1B1464")
    or_logo_label.place(x=10, y=600)
except FileNotFoundError:
    tk.Label(left_frame, text="OR LOGO", bg="#1B1464", fg="white", font=("PTT 45 Pride", 12)).place(x=10, y=10)

# ส่วนขวา (สีขาว)
right_frame = tk.Frame(root, bg="white", width=300, height=400)
right_frame.pack(side="right", fill="both", expand=True)

# ใส่โลโก้ด้านบน (ปรับให้แสดงรูปภาพ)
try:
    water_logo_path = os.path.join(icon_dir, "about-logo.png")  # Path ของภาพ
    water_logo_image = Image.open(water_logo_path)  # เปิดไฟล์ภาพ
    sizeX_logo = int(200*(1/3))
    sizeY_logo = int(200*(1/2))
    water_logo_image = water_logo_image.resize((sizeX_logo, sizeY_logo), Image.Resampling.LANCZOS)  # ปรับขนาด
    water_logo_photo = ImageTk.PhotoImage(water_logo_image)  # แปลงเป็น PhotoImage
    water_logo_label = tk.Label(right_frame, image=water_logo_photo, bg="white")
    water_logo_label.pack(pady=(20, 150))
except FileNotFoundError:
    tk.Label(right_frame, text="WATER LOGO", bg="white", fg="black", font=("PTT 45 Pride", 12)).pack(pady=20)

# ข้อความ "Get Started"
get_started_label = tk.Label(right_frame, text="Get started", bg="white", fg="black", font=("PTT 45 Pride", 24, "bold"))
get_started_label.pack(pady=10)

# ปุ่ม Log In
login_button = tk.Button(right_frame, text="Log in", bg="#007BFF", fg="white", font=("PTT 45 Pride", 12),
                         width=12, command=login)
login_button.pack(pady=5)

# ปุ่ม Sign Up
signup_button = tk.Button(right_frame, text="Sign up", bg="#007BFF", fg="white", font=("PTT 45 Pride", 12),
                          width=12, command=signup)
signup_button.pack(pady=5)

# ปุ่ม Guest
guest_button = tk.Button(right_frame, text="Guest", bg="white", fg="black", font=("PTT 45 Pride", 12),
                         width=12, command=guest, relief="flat")
guest_button.pack(pady=5)

# ปุ่ม Log out
logout_button = tk.Button(right_frame, text="Log out", bg="#FF0000", fg="white", font=("PTT 45 Pride", 12),
                          width=12, command=logout)
logout_button.pack(pady=20)

# เริ่มต้นโปรแกรม
root.mainloop()
