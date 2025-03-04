import tkinter as tk
from tkinter import messagebox
from matplotlib import pyplot as plt
from home_frame import HomeFrame
from community_frame import CommunityFrame
from dashboard_frame import DashboardFrame
from leaderboard_frame import LeaderboardFrame
from setting_frame import SettingFrame
from PDPA_frame import PopupFrame
from profile_frame import ProfileFrame
from decimal import Decimal
from PIL import Image, ImageTk
import win32gui
import win32con
import time
import os
import requests
import sys
import threading
import subprocess

def change_windows_taskbar_icon(window, icon_windows_path):
    try:
        window.iconbitmap(icon_windows_path)  # ใช้พารามิเตอร์ที่ถูกต้อง
    except Exception as e:
        print(f"Error changing icon: {e}")

class App(tk.Tk):
    def __init__(self, user_email):
        super().__init__()

        self.running = True

        # กำหนด path สำหรับไอคอนทั้งหมด
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        self.icon_windows_path = os.path.join(self.icon_dir, "windows_icon.ico")
        change_windows_taskbar_icon(self, self.icon_windows_path)
        self.change_taskbar_icon()
        self.title("ERGO PROJECT")
        # ตั้งค่าไอคอน
        self.iconbitmap(os.path.join(self.icon_dir, "GODJI-Action_200113_0008.ico"))  # เปลี่ยนเป็นพาธของไฟล์ .ico
        self.geometry("1024x768")  # ขนาดหน้าต่าง
        self.configure(bg="white")  # สีพื้นหลังหน้าต่างหลัก
        window_width = 1024
        window_height = 768
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")
        self.start_time = None
        self.app_time = Decimal("0.00")
        
        self.start_timer()  # เริ่มจับเวลาเมื่อเปิดแอป
        # ดักจับ event ปิดแอป
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # response = requests.get("http://127.0.0.1:8000/users")
        # if response.status_code == 200:
        #     data = response.json()
        #     self.username = data['users'][3]
        
        self.user_email = user_email
    
        # 🔹 ดึงรายชื่อ users จาก API
        response = requests.get("http://127.0.0.1:8000/users")
        if response.status_code == 200:
            try:
                data = response.json()

                # พิมพ์ข้อมูลที่ได้รับจาก API
                # print("Users list from API:", data)

                # ตรวจสอบว่า 'users' มีอยู่ และเป็น list
                users_list = data.get('users', [])
                if isinstance(users_list, list):
                    # 🔹 ค้นหา user ตาม email
                    user_data = next((user for user in users_list if user.get("email") == self.user_email), None)

                    if user_data:
                        self.username = user_data.get("username", "Unknown User")
                    else:
                        self.username = "Unknown User"

                    print(f"🔹 Username: {self.username}")
                else:
                    print("⚠️ Error: 'users' is not a list!")
                    self.username = "Unknown User"
            except ValueError as e:
                print(f"⚠️ Error: Failed to parse response as JSON - {e}")
                self.username = "Unknown User"
        else:
            print(f"⚠️ API Error: {response.status_code}")
            self.username = "Unknown User"
            
        
        self.show_popup()
        
        # ฟังก์ชันที่จะได้รับค่าภาษา
        self.selected_language = "English"
        
        # สร้าง SettingFrame และส่งฟังก์ชัน callback ไป
        self.setting_frame = SettingFrame(self, self.get_is_muted, self.on_language_change)
        self.setting_frame.place(x=0, y=0, width=800, height=400)

        self.translations = {
            "English": {
                "home": "Home",
                "community": "Community",
                "dashboard": "Dashboard",
                "leaderboard": "Leaderboard",
            },
            "ภาษาไทย": {
                "home": "หน้าแรก",
                "community": "ชุมชน",
                "dashboard": "แผงควบคุม",
                "leaderboard": "การจัดอันดับ",
            },
        }
        
        self.frames = {}
        self.current_frame = None

        # Sidebar
        self.sidebar = tk.Frame(self, bg="#221551", width=200, height=768)  # กำหนดความสูง
        self.sidebar.pack(side="left", fill="y")  # แพ็ค sidebar ทางด้านซ้าย

        # Username Display with Profile Picture
        self.username_frame = tk.Frame(self.sidebar, bg="#221551", height=200)
        self.username_frame.place(x=0, y=0, width=200)  # ใช้ place แทน pack

        # Label ที่จะใช้แสดงข้อความ "MENU" เมื่อหน้าต่างเล็ก
        self.menu_label = tk.Label(self.sidebar, text="M\nE\nN\nU", bg="#221551", fg="white", font=("Arial", 20))
        self.menu_label.place(x=20, y=220)

        # ซ่อน label "MENU" เมื่อเริ่ม
        self.menu_label.place_forget()

        # Binding the window resize event to a function
        self.bind("<Configure>", self.on_resize)
        
        # ฟังก์ชันตัดคำตามช่องว่าง
        def wrap_text(text, width):
            words = text.split(" ")
            lines = []
            current_line = ""

            for word in words:
                if len(current_line) + len(word) + 1 <= width:
                    current_line += " " + word if current_line else word
                else:
                    lines.append(current_line)
                    current_line = word

            if current_line:
                lines.append(current_line)

            return "\n".join(lines)

        wrapped_username = wrap_text(self.username, 15)

        # แสดงข้อความ Username พร้อมตัดคำ
        tk.Label(self.username_frame, text=wrapped_username, font=("PTT 45 Pride", 14), fg="white", bg="#221551", wraplength=180, justify="center").place(x=10, y=150)


        # สร้างปุ่ม Home
        home_icon_path = os.path.join(self.icon_dir, "home_icon.png")
        home_icon = tk.PhotoImage(file=home_icon_path)

        self.home_button = tk.Button(
            self.sidebar,
            image=home_icon,
            text=self.translations[self.selected_language]["home"],
            compound="left",  # แสดงไอคอนทางซ้ายของข้อความ
            bg="#221551",
            fg="white",
            font=("PTT 45 Pride", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(HomeFrame),
        )
        self.home_button.image = home_icon
        self.home_button.place(x=30, y=250)  # ปรับตำแหน่งปุ่ม Home

        # สร้างปุ่ม Community
        community_icon_path = os.path.join(self.icon_dir, "community_icon.png")
        community_icon = tk.PhotoImage(file=community_icon_path)

        self.community_button = tk.Button(
            self.sidebar,
            image=community_icon,
            text=self.translations[self.selected_language]["community"],
            compound="left",
            bg="#221551",
            fg="white",
            font=("PTT 45 Pride", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(CommunityFrame),
        )
        self.community_button.image = community_icon
        self.community_button.place(x=30, y=350)  # ปรับตำแหน่งปุ่ม Community

        # สร้างปุ่ม Dashboard
        dashboard_icon_path = os.path.join(self.icon_dir, "Dashboard_icon.png")
        dashboard_icon = tk.PhotoImage(file=dashboard_icon_path)

        self.dashboard_button = tk.Button(
            self.sidebar,
            image=dashboard_icon,
            text=self.translations[self.selected_language]["dashboard"],
            compound="left",
            bg="#221551",
            fg="white",
            font=("PTT 45 Pride", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(DashboardFrame),
        )
        self.dashboard_button.image = dashboard_icon
        self.dashboard_button.place(x=30, y=450)  # ปรับตำแหน่งปุ่ม Dashboard

        # สร้างปุ่ม Leaderboard
        leaderboard_icon_path = os.path.join(self.icon_dir, "Leaderboard_icon.png")
        leaderboard_icon = tk.PhotoImage(file=leaderboard_icon_path)

        self.leaderboard_button = tk.Button(
            self.sidebar,
            image=leaderboard_icon,
            text=self.translations[self.selected_language]["leaderboard"],
            compound="left",
            bg="#221551",
            fg="white",
            font=("PTT 45 Pride", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(LeaderboardFrame),
        )
        self.leaderboard_button.image = leaderboard_icon
        self.leaderboard_button.place(x=30, y=550)  # ปรับตำแหน่งปุ่ม Leaderboard

        # สร้างปุ่ม Setting
        setting_icon_path = os.path.join(self.icon_dir, "Settings_icon 1.png")
        setting_icon = tk.PhotoImage(file=setting_icon_path)

        self.setting_button = tk.Button(
            self.sidebar,
            image=setting_icon,
            compound="left",  # แสดงไอคอนทางซ้ายของข้อความ
            bg="#221551",
            fg="white",
            font=("PTT 45 Pride", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(SettingFrame),
        )
        self.setting_button.image = setting_icon
        self.setting_button.place(x=50, y=650)  # ปรับตำแหน่งปุ่ม Setting

        # สร้างสถานะสำหรับปุ่ม speaker
        self.is_muted = False

        # สร้างปุ่ม speaker
        self.speaker_icon_path = os.path.join(self.icon_dir, "Speaker.png")
        self.mute_icon_path = os.path.join(self.icon_dir, "mute.png")

        self.speaker_icon = tk.PhotoImage(file=self.speaker_icon_path)
        self.mute_icon = tk.PhotoImage(file=self.mute_icon_path)

        # ลบการสร้างปุ่ม speaker ซ้ำ
        # ปุ่มนี้ได้ถูกสร้างไว้ในตอนแรกแล้ว
        self.speaker_button = tk.Button(
            self.sidebar,
            image=self.speaker_icon,
            compound="left",  # แสดงไอคอนทางซ้ายของข้อความ
            bg="#221551",
            fg="white",
            font=("Arial", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=self.toggle_mute,  # เชื่อมต่อฟังก์ชัน toggle_mute
        )
        self.speaker_button.image = self.speaker_icon
        self.speaker_button.place(x=104, y=641)  # ปรับตำแหน่งปุ่ม speaker

        

        from PIL import Image, ImageTk  # เพิ่มการนำเข้า Pillow

        # โหลดและปรับขนาดรูปภาพ
        profile_icon_path = os.path.join(self.icon_dir, "profile.png")
        profile_image = Image.open(profile_icon_path)
        profile_image = profile_image.resize((100, 100), Image.Resampling.LANCZOS)  # ใช้ LANCZOS แทน ANTIALIAS
        profile_icon = ImageTk.PhotoImage(profile_image)

        # สร้างปุ่ม profile
        self.profile_button = tk.Button(
            self.sidebar,
            image=profile_icon,
            compound="left",  # แสดงไอคอนทางซ้ายของข้อความ
            bg="#221551",
            fg="white",
            font=("PTT 45 Pride", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(ProfileFrame),
        )
        self.profile_button.image = profile_icon
        self.profile_button.place(x=55, y=10)  # ปรับตำแหน่งปุ่ม

        # Default frame
        self.show_frame(HomeFrame)
        
    def change_taskbar_icon(self):
        # เปลี่ยนไอคอน Taskbar โดยใช้ win32gui
        icon_path = os.path.join(self.icon_dir, "GODJI-Action_200113_0008.ico")
        hwnd = win32gui.GetForegroundWindow()
        win32gui.SendMessage(hwnd, win32con.WM_SETICON, win32con.ICON_SMALL, icon_path)

    def toggle_mute(self):
        """สลับสถานะเสียงและอัปเดตไอคอนปุ่ม"""
        self.is_muted = not self.is_muted  # สลับสถานะ

        if self.is_muted:
            self.speaker_button.config(image=self.mute_icon)  # เปลี่ยนเป็นไอคอน mute
        else:
            self.speaker_button.config(image=self.speaker_icon)  # เปลี่ยนกลับเป็นไอคอน speaker

    def load_sidebar_profile_image(self):
        """ โหลดรูปโปรไฟล์ Sidebar และอัปเดตปุ่ม """

        profile_icon_path = os.path.join(self.icon_dir, "profile.png")
        if not os.path.exists(profile_icon_path):
            profile_icon_path = os.path.join(self.icon_dir, "default_profile.png")
        profile_image = Image.open(profile_icon_path)
        profile_image = profile_image.resize((100, 100), Image.Resampling.LANCZOS)
        profile_icon = ImageTk.PhotoImage(profile_image)
        if self.profile_button:
            self.profile_button.config(image=profile_icon)
            self.profile_button.image = profile_icon
    
        else:
            self.profile_button = tk.Button(
            self.sidebar,
            image=profile_icon,
            compound="left",
            bg="#221551",
            fg="white",
            font=("Arial", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(ProfileFrame),
        )
        self.profile_button.place(x=55, y=10)
        self.profile_button.image = profile_icon

    
    def update_sidebar_profile(self, new_image_path):
        """ Callback เมื่อรูปโปรไฟล์เปลี่ยน """
        self.load_sidebar_profile_image()

    def show_frame(self, frame_class): 
        # ถ้าเฟรมที่ต้องการแสดงคือเฟรมเดียวกับที่แสดงอยู่แล้ว
        if self.current_frame and isinstance(self.current_frame, frame_class):
            return  # ไม่ต้องเปลี่ยนถ้าเป็นเฟรมเดิม

        # ซ่อนเฟรมปัจจุบัน
        if self.current_frame:
            self.current_frame.pack_forget()  # ใช้ pack_forget เพื่อซ่อนเฟรมเดิม

        # สร้างเฟรมใหม่หากยังไม่มี
        if frame_class not in self.frames:
            if frame_class == SettingFrame:
                self.frames[frame_class] = frame_class(self, self.get_is_muted, self.on_language_change)

            elif frame_class == DashboardFrame:
                self.frames[frame_class] = frame_class(self, self.user_email)  # ส่ง email ไปให้ DashboardFrame
            
            elif frame_class == CommunityFrame:
                self.frames[frame_class] = frame_class(self, self.user_email)

            elif frame_class == ProfileFrame:
                self.frames[frame_class] = frame_class(self, self.user_email, app_instance=self)  # ส่ง email ไปให้ ProfileFrame    

            else:
                self.frames[frame_class] = frame_class(self)

        # ตั้งค่าเฟรมใหม่เป็นเฟรมปัจจุบัน
        self.current_frame = self.frames[frame_class]

        # วางเฟรมใหม่
        self.current_frame.pack(fill=tk.BOTH, expand=True)  # fill=tk.BOTH จะทำให้เฟรมขยายทั้งในแนวนอนและแนวตั้ง


    def get_is_muted(self):
        """คืนค่าตัวแปร is_muted"""
        return self.is_muted

    def on_language_change(self, language):
        print(f"Language changed to: {language}")
        self.selected_language = language
        self.update_language(language)
    
    def show_popup(self):
        PopupFrame(self) 

        
    def update_language(self, language):
        self.selected_language = language
        self.home_button.config(text=self.translations[self.selected_language]["home"])
        self.community_button.config(text=self.translations[self.selected_language]["community"])
        self.dashboard_button.config(text=self.translations[self.selected_language]["dashboard"])
        self.leaderboard_button.config(text=self.translations[self.selected_language]["leaderboard"])
        
    def on_resize(self, event):
        # ใช้ self.winfo_width() เพื่อรับค่าความกว้างปัจจุบันของหน้าต่าง
        if self.winfo_width() < 700:
            # ย่อ sidebar ในแกน x
            self.sidebar.config(width=60)  # ย่อ sidebar ให้แคบลง
            self.menu_label.place(x=20, y=220)  # แสดงข้อความ "MENU"
            
            # ซ่อนปุ่มเมนู
            self.username_frame.place_forget()
            self.profile_button.place_forget()
            self.home_button.place_forget()
            self.community_button.place_forget()
            self.dashboard_button.place_forget()
            self.leaderboard_button.place_forget()
            self.setting_button.place_forget()
            self.speaker_button.place_forget()
            
        else:
            # ขยาย sidebar กลับไปที่ขนาดเดิม
            self.sidebar.config(width=200)
            self.menu_label.place_forget()  # ซ่อนข้อความ "MENU"
            
            # แสดงปุ่มเมนู
            self.profile_button.place(x=20, y=20)
            self.username_frame.place(x=0, y=0, width=200) 
            self.home_button.place(x=30, y=250)
            self.community_button.place(x=30, y=350)
            self.dashboard_button.place(x=30, y=450)
            self.leaderboard_button.place(x=30, y=550)
            self.setting_button.place(x=50, y=650)
            self.speaker_button.place(x=104, y=641)

    def start_timer(self):
        """เริ่มจับเวลาเมื่อเปิดแอป"""
        self.start_time = time.time()
        print("Started app timer.")

    def stop_timer(self):
        """หยุดจับเวลาเมื่อปิดแอปและบันทึกเวลาใช้งาน"""
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            self.app_time = Decimal(f"{elapsed_time:.2f}")
            self.send_app_time()
            self.send_app_time_month()
            print(f"App closed. Total usage time: {self.app_time} seconds")
        else:
            print("Timer was not started.")
            
    def send_app_time(self):
        """ส่งค่าการใช้งานแอปไปยัง API"""
        api_url = "http://127.0.0.1:8000/update_app_time/"
        params = {
            "email": self.user_email,
            "app_time": float(self.app_time)  # แปลงเป็น float ก่อนส่ง
        }
        try:
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                print("✅ App time updated successfully:", response.json())
            else:
                print("❌ Failed to update app time:", response.json())
        except Exception as e:
            print(f"❌ Error sending data: {e}")
    
    # เริ่ม Task เบื้องหลัง
        self.bg_thread = threading.Thread(target=self.background_task, daemon=True)
        self.bg_thread.start()
    
    def send_app_time_month(self):
        """ส่งค่าการใช้งานแอปไปยัง API"""
        api_url = "http://127.0.0.1:8000/update_app_time_month/"  # เปลี่ยน endpoint
        params = {
            "email": self.user_email,
            "app_time": float(self.app_time)  # แปลงเป็น float ก่อนส่ง
        }
        try:
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                print("✅ App time updated successfully:", response.json())
            else:
                print("❌ Failed to update app time:", response.json())
        except Exception as e:
            print(f"❌ Error sending data: {e}")

        # เริ่ม Task เบื้องหลัง
        self.bg_thread = threading.Thread(target=self.background_task, daemon=True)
        self.bg_thread.start()

    def on_closing(self):
        """ซ่อน UI และให้ Background Task ทำงานต่อ"""
        self.running = False  # ✅ หยุด Background Task
        self.withdraw()  # ซ่อนหน้าต่างหลัก
        self.stop_timer()  # หยุดจับเวลา
        print("App is running in the background...")

    def background_task(self):
        """ทำงานต่อแม้ UI ถูกซ่อน"""
        while self.running:
            print("Background task running...")
            time.sleep(5) # หยุดเพื่อป้องกันการใช้ CPU มากเกินไป แสเดงว่าเป็นวินาที
        print("Background task stopped.")
        
def open_login():
    """เปิดหน้าต่าง Login ใหม่โดยไม่ต้องนำเข้า LoginApp"""
    # ตรวจสอบว่าไฟล์ Login.py อยู่ในตำแหน่งที่ถูกต้อง
    login_py_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "Login.py"))
    if not os.path.exists(login_py_path):
        messagebox.showerror("Error", "Cannot find Login.py")
        return

    try:
        print(f"✅ เปิด Login.py ที่พาธ: {login_py_path}")
        python_executable = sys.executable  # ใช้ Python interpreter เดียวกัน
        subprocess.Popen([python_executable, login_py_path], shell=True)  # ใช้ shell=True ช่วยให้ทำงานได้ดีขึ้น

        print("🛑 บังคับปิดแอปหลักด้วย sys.exit()")
        sys.exit()  # ปิดแอปหลักไปเลย

    except Exception as e:
        messagebox.showerror("Error", f"Failed to open Login: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_email = sys.argv[1]  # ✅ ดึง email จาก arguments
        app = App(user_email)
        app.mainloop()
    else:
        open_login()
        print("Error: No user email provided.")