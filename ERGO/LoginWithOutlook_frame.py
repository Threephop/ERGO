import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from msal import PublicClientApplication
import webbrowser
import os

# Microsoft App Configuration
CLIENT_ID = "e05e1663-bc57-4c87-ab60-d41463b12dcb"
AUTHORITY = "https://login.microsoftonline.com/8c1832ea-a96d-413e-bf7d-9fe4d608e00b"
REDIRECT_URI = "http://localhost:3000"
SCOPES = ["User.Read"]
icon_dir = os.path.join(os.path.dirname(__file__), "icon")

# ฟังก์ชัน Log in
def login():
    app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
    try:
        # แก้ไขการเรียก acquire_token_interactive
        auth_result = app.acquire_token_interactive(scopes=SCOPES)  # ลบ redirect_uri
        if "access_token" in auth_result:
            messagebox.showinfo("Login Success", f"Welcome! Token: {auth_result['access_token']}")
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
        login()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during logout: {e}")

# สร้างหน้าต่างหลัก
root = tk.Tk()
root.title("ERGO PROJECT")
root.geometry("600x400")
root.configure(bg="black")

# ส่วนซ้าย (สีพื้นหลังน้ำเงิน)
left_frame = tk.Frame(root, bg="#1B1464", width=300, height=400)
left_frame.pack(side="left", fill="y")

# ใส่โลโก้ OR (ปรับให้แสดงรูปภาพ)
try:
    or_logo_path = os.path.join(icon_dir, "PTT-Logo.png")  # Path ของภาพ
    or_logo_image = Image.open(or_logo_path)  # เปิดไฟล์ภาพ
    or_logo_image = or_logo_image.resize((100, 50), Image.Resampling.LANCZOS)  # ปรับขนาด
    or_logo_photo = ImageTk.PhotoImage(or_logo_image)  # แปลงเป็น PhotoImage
    or_logo_label = tk.Label(left_frame, image=or_logo_photo, bg="#1B1464")
    or_logo_label.place(x=10, y=10)
except FileNotFoundError:
    tk.Label(left_frame, text="OR LOGO", bg="#1B1464", fg="white", font=("Arial", 12)).place(x=10, y=10)

# ส่วนขวา (สีขาว)
right_frame = tk.Frame(root, bg="white", width=300, height=400)
right_frame.pack(side="right", fill="both", expand=True)

# ใส่โลโก้ด้านบน (ปรับให้แสดงรูปภาพ)
try:
    water_logo_path = os.path.join(icon_dir, "about-logo.png")  # Path ของภาพ
    water_logo_image = Image.open(water_logo_path)  # เปิดไฟล์ภาพ
    water_logo_image = water_logo_image.resize((80, 80), Image.Resampling.LANCZOS)  # ปรับขนาด
    water_logo_photo = ImageTk.PhotoImage(water_logo_image)  # แปลงเป็น PhotoImage
    water_logo_label = tk.Label(right_frame, image=water_logo_photo, bg="white")
    water_logo_label.pack(pady=20)
except FileNotFoundError:
    tk.Label(right_frame, text="WATER LOGO", bg="white", fg="black", font=("Arial", 12)).pack(pady=20)

# ข้อความ "Get Started"
get_started_label = tk.Label(right_frame, text="Get started", bg="white", fg="black", font=("Arial", 16, "bold"))
get_started_label.pack(pady=10)

# ปุ่ม Log In
login_button = tk.Button(right_frame, text="Log in", bg="#007BFF", fg="white", font=("Arial", 12),
                         width=12, command=login)
login_button.pack(pady=5)

# ปุ่ม Sign Up
signup_button = tk.Button(right_frame, text="Sign up", bg="#007BFF", fg="white", font=("Arial", 12),
                          width=12, command=signup)
signup_button.pack(pady=5)

# ปุ่ม Guest
guest_button = tk.Button(right_frame, text="Guest", bg="white", fg="black", font=("Arial", 12),
                         width=12, command=guest, relief="flat")
guest_button.pack(pady=5)

# ปุ่ม Log out
logout_button = tk.Button(right_frame, text="Log out", bg="#FF0000", fg="white", font=("Arial", 12),
                          width=12, command=logout)
logout_button.pack(pady=20)

# เริ่มต้นโปรแกรม
root.mainloop()
