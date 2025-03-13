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
import io
import psutil
import pystray
from PIL import Image, ImageDraw
import win32api
import win32event
import win32process
import winerror
import ctypes
from ctypes import wintypes

def change_windows_taskbar_icon(window, icon_windows_path):
    try:
        window.iconbitmap(icon_windows_path)  # ใช้พารามิเตอร์ที่ถูกต้อง
    except Exception as e:
        print(f"Error changing icon: {e}")
        
params = {
    "x_api_key": "ergoapipoC18112024",  # ส่ง API Key ใน query parameter
}

class App(tk.Tk):
    def __init__(self, user_email):
        super().__init__()
        self.running = True
        # เพิ่มการจัดการการทำงานร่วมกับ Windows Taskbar
        self.protocol("WM_TAKE_FOCUS", self.on_taskbar_click)
        self.after(100, self.register_taskbar_restart)

        # กำหนด path สำหรับไอคอนทั้งหมด
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        self.icon_windows_path = os.path.join(self.icon_dir, "windows_icon.ico")
        change_windows_taskbar_icon(self, self.icon_windows_path)
        self.change_taskbar_icon()
        self.title("ERGO PROJECT")
        self.user_email = user_email
        self.user_id = None  # เก็บ user_id
        self.profile_image_url = None  # ✅ ป้องกัน AttributeError
    
        self.user_id = self.fetch_user_id(user_email)  # ดึง user_id จาก API
        
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        # ตั้งค่าไอคอน
        self.default_profile_path = os.path.join(self.icon_dir, "profile.png")
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

        # response = requests.get("https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io/users")
        # if response.status_code == 200:
        #     data = response.json()
        #     self.username = data['users'][3]
        
    
        # ดึงรายชื่อ users จาก API
        try:
            response = requests.get("https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io/users", params=params, timeout=5)
            response.raise_for_status()  # ตรวจสอบ HTTP Status Code

            data = response.json()

            # ตรวจสอบว่า 'users' มีอยู่ และเป็น list
            users_list = data.get('users', [])
            if isinstance(users_list, list):
                # 🔹 ค้นหา user ตาม email
                user_data = next((user for user in users_list if user.get("email") == self.user_email), None)
                self.username = user_data.get("username", "Unknown User") if user_data else "Unknown User"
            else:
                print("⚠️ Error: 'users' is not a list!")
                self.username = "Unknown User"

        except (requests.RequestException, ValueError) as e:
            print(f"⚠️ API Error: {e}")
            self.username = "Unknown User"
            self.show_popup()  # แสดง Popup สำหรับเลือกวิดีโอ

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
        
        # ✅ สร้าง Sidebar ก่อน (แต่ยังไม่โหลดรูป)
        self.sidebar = tk.Frame(self, bg="#221551", width=200, height=768)
        self.sidebar.pack(side="left", fill="y")

        # ✅ สร้างปุ่ม Profile ก่อน แล้วโหลดรูปภายหลัง
        self.profile_button = tk.Button(
            self.sidebar,
            bg="#221551",
            fg="white",
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(ProfileFrame),
        )
        self.profile_button.place(x=55, y=10)  # ปรับตำแหน่งปุ่ม

        # ✅ โหลดรูปโปรไฟล์จาก API หลังจากสร้างปุ่มแล้ว
        self.update_sidebar_profile()

        self.frames = {}
        self.current_frame = None

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


        # สร้างปุ่ม Profile ก่อน แล้วโหลดรูปภายหลัง
        self.profile_button = tk.Button(
            self.sidebar,
            bg="#221551",
            fg="white",
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(ProfileFrame),
        )
        self.profile_button.place(x=60, y=10)  # ปรับตำแหน่งปุ่ม

        # โหลดรูปโปรไฟล์จาก API หลังจากสร้างปุ่มแล้ว
        self.update_sidebar_profile()
        self.show_frame(HomeFrame)
    
    def fetch_profile_image(self):
        """ ดึง URL รูปโปรไฟล์จาก API แล้วบันทึกไว้ที่ self.profile_image_url """
        def fetch():
            api_url = f"https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io/get_profile_url/{self.user_id}"
            try:
                response = requests.get(api_url, params=params, timeout=5)
                if response.status_code == 200:
                    self.profile_image_url = response.json().get("profile_url", "")
                    print(f"✅ Profile image URL updated: {self.profile_image_url}")
                    self.after(2000, self.update_sidebar_profile)  # ✅ รอให้ API อัปเดตก่อนโหลดรูป
                else:
                    print("⚠️ API returned error for profile image")
                    self.profile_image_url = None
            except requests.RequestException as e:
                print(f"⚠️ Error fetching profile image: {e}")
                self.profile_image_url = None

        threading.Thread(target=fetch, daemon=True).start()

    def fetch_user_id(self, email):
        url = f"https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io/get_user_id/{email}"
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get("user_id")  # ✅ ส่งค่า user_id กลับไปทันที
            else:
                return None
        except requests.RequestException as e:
            print(f"⚠️ Error fetching user_id: {e}")
            return None
    
    def update_sidebar_profile(self):
        """โหลดและอัปเดตรูปโปรไฟล์ที่ Sidebar"""
        try:
            # ✅ 1. ดึง URL ของรูปโปรไฟล์จาก API
            response = requests.get("https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io/get_profile_image/", params={"user_id": self.user_id, "x_api_key": "ergoapipoC18112024"})
            profile_url = response.json().get("profile_url") if response.status_code == 200 else None

            # ✅ 2. โหลดรูปจาก URL (ถ้ามี)
            if profile_url:
                try:
                    image_response = requests.get(profile_url, params=params, timeout=5)
                    if image_response.status_code == 200:
                        image_data = io.BytesIO(image_response.content)
                        profile_image = Image.open(image_data)
                    else:
                        raise ValueError("Failed to fetch image from URL")
                except Exception as e:
                    print(f"⚠️ Error loading profile image from URL: {e}")
                    profile_image = Image.open(self.default_profile_path)  # 🔹 ใช้ Default
            else:
                profile_image = Image.open(self.default_profile_path)  # 🔹 ใช้ Default ถ้าไม่มี URL

            # ✅ 3. ปรับขนาดรูปภาพ
            profile_image = profile_image.resize((100, 100), Image.Resampling.LANCZOS)
            profile_icon = ImageTk.PhotoImage(profile_image)

            # ✅ 4. อัปเดตปุ่ม Sidebar
            self.profile_button.config(image=profile_icon)
            self.profile_button.image = profile_icon  # ✅ ป้องกันการรีเฟอเรนซ์หาย
            print("✅ Sidebar profile updated successfully!")

        except Exception as e:
            print(f"❌ update_sidebar_profile() error: {e}")



    def on_profile_picture_updated(self):
        """อัปเดตรูปโปรไฟล์ใหม่หลังจากเปลี่ยนรูป"""
        print("✅ Profile picture updated, refreshing sidebar...")

        # 🔹 เรียก API refresh_profile เพื่อดึงค่าล่าสุด
        try:
            api_url = f"https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io/refresh_profile/{self.user_id}"
            response = requests.get(api_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            # 🔹 อัปเดต Username และ Profile Image URL
            self.username = data.get("username", "Unknown User")
            self.profile_image_url = data.get("profile_url")

            # 🔹 โหลดรูปโปรไฟล์ใหม่ใน Sidebar
            self.update_sidebar_profile()

        except requests.RequestException as e:
            print(f"⚠️ Failed to refresh profile: {e}")
        
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
        """ โหลดรูปโปรไฟล์จาก URL และอัปเดต Sidebar """
        profile_icon = None  # 🔹 กำหนดค่า Default ก่อน
        profile_url = self.fetch_profile_image()  # ดึง URL ของโปรไฟล์จาก API
        
        if profile_url:
            try:
                response = requests.get(profile_url, params=params, timeout=5)  # โหลดรูปจาก URL
                if response.status_code == 200:
                    image_data = io.BytesIO(response.content)
                    image = Image.open(image_data)
                    image = image.resize((100, 100), Image.Resampling.LANCZOS)
                    profile_icon = ImageTk.PhotoImage(image)  
                else:
                    raise ValueError("Failed to fetch image from URL")
            except Exception as e:
                print(f"⚠️ Error loading profile image from URL: {e}")

        # 🔹 ถ้าโหลดจาก URL ไม่สำเร็จ ให้ใช้ Default `profile.png`
        if profile_icon is None:
            profile_icon = ImageTk.PhotoImage(Image.open(os.path.join(self.icon_dir, "profile.png")).resize((100, 100)))

        if hasattr(self, 'profile_button'):
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
            self.profile_button.image = profile_icon
            self.profile_button.place(x=60, y=10)


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
                 
            elif frame_class == LeaderboardFrame:
                self.frames[frame_class] = frame_class(self, self.user_email)
                
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
            self.profile_button.place(x=50, y=20)
            self.username_frame.place(x=25, y=0, width=200) 
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
        api_url = "https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io/update_app_time/"
        params = {
            "email": self.user_email,
            "app_time": float(self.app_time),  # แปลงเป็น float 
            "x_api_key": "ergoapipoC18112024"
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
    # สร้าง System Tray Icon 
        self.create_tray_icon()

        if self.is_already_running():
            print("โปรแกรมกำลังทำงานอยู่แล้ว!")
            sys.exit(1)

    def send_app_time_month(self):
        """ส่งค่าการใช้งานแอปไปยัง API"""
        api_url = "https://ergoapicontainer.kindfield-b150dbf6.southeastasia.azurecontainerapps.io/update_app_time_month/"  # เปลี่ยน endpoint
        params = {
            "email": self.user_email,
            "app_time": float(self.app_time),  # แปลงเป็น float ก่อนส่ง
            "x_api_key": "ergoapipoC18112024"
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
        self.running = True  # ยังให้ Background Task ทำงานต่อ
        self.withdraw()  # ซ่อนหน้าต่างหลัก
        
        # อัปเดตเวลาล่าสุดก่อนที่จะซ่อน
        elapsed_time = time.time() - self.start_time
        self.app_time = Decimal(f"{elapsed_time:.2f}")
        self.send_app_time()
        
        # restart timer เพื่อให้นับต่อเมื่อกลับมา
        self.start_time = time.time()
        
        self.create_tray_icon()  # สร้าง System Tray Icon ถ้ายังไม่มี
        print("App is running in the background...")
        return "break"  # ป้องกันการปิดแอปโดยสิ้นเชิง

    def background_task(self):
        """ทำงานต่อแม้ UI ถูกซ่อน"""
        while self.running:
            print("Background task running...")
            time.sleep(10) # หยุดเพื่อป้องกันการใช้ CPU มากเกินไป แสเดงว่าเป็นวินาที
        print("Background task stopped.")

    def create_tray_icon(self):
        """สร้างไอคอนใน System Tray จากไฟล์ ICO"""
        if hasattr(self, 'tray_icon'):
            return  # ถ้ามี tray_icon อยู่แล้ว ไม่ต้องสร้างใหม่

        icon_path = os.path.join(self.icon_dir, "windows_icon.ico")
        if not os.path.exists(icon_path):
            print(f"❌ ไม่พบไฟล์ไอคอนที่ '{icon_path}'")
            icon_path = os.path.join(self.icon_dir, "GODJI-Action_200113_0008.ico")  # ลองใช้ไอคอนอื่น
            if not os.path.exists(icon_path):
                return

        icon_image = Image.open(icon_path)

        # ฟังก์ชันการตอบสนองต่อการคลิกที่ไอคอน
        def on_left_click(icon, item):
            self.show_window()

        # กำหนดเมนู Tray
        menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Exit", self.exit_app)
        )

        self.tray_icon = pystray.Icon("ergo_project", icon_image, "ERGO PROJECT", menu)
        
        # กำหนดการตอบสนองต่อการคลิก (รวมทั้งดับเบิลคลิก)
        self.tray_icon.on_activate = on_left_click
        
        # รัน Tray Icon ใน Thread แยก
        self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
        self.tray_thread.start()


    def show_window(self, icon=None, item=None):
        """เปิดหน้าต่างหลักกลับมา"""
        self.deiconify()  # แสดงหน้าต่างหลัก
        self.lift()  # นำหน้าต่างมาด้านหน้า
        self.focus_force()  # บังคับให้ได้รับ focus
        
        # บันทึกเวลาที่ใช้ในการทำงานเบื้องหลัง
        if self.start_time is not None:
            elapsed_time = time.time() - self.start_time
            self.app_time += Decimal(f"{elapsed_time:.2f}")
            
        # เริ่มจับเวลาใหม่
        self.start_time = time.time()

    def exit_app(self):
        """ปิดแอปทั้งหมด รวมถึง Background Task"""
        print("🛑 Exiting application...")

        # หยุด Background Task
        self.running = False  

        # ปิด System Tray Icon ถ้ามี
        if hasattr(self, 'tray_icon'):
            self.tray_icon.stop()

        # ปิดหน้าต่างหลักจาก main thread
        self.after(100, self.destroy)  

        # ปิดโปรเซสทั้งหมด
        self.after(200, sys.exit, 0)  # ให้ Tkinter ปิดก่อน แล้วค่อยออกจากโปรแกรม

    def is_already_running(self):
        """เช็คว่าโปรแกรมกำลังทำงานอยู่หรือไม่ และเปิดหน้าต่างเดิมแทน"""
        current_pid = os.getpid()
        current_exe = sys.executable
        
        for process in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if (process.info['name'] == os.path.basename(current_exe) or 
                    process.info['exe'] == current_exe) and process.info['pid'] != current_pid:
                    
                    print(f"🔍 Found running instance: PID {process.info['pid']}")
                    if self.focus_existing_window(process.info['pid']):
                        return True  # พบโปรแกรมที่เปิดอยู่ และนำกลับมาแสดงแล้ว
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def focus_existing_window(self, pid):
        """หาหน้าต่างของโปรแกรมที่มีอยู่ และนำกลับมาแสดง"""
        def callback(hwnd, hwnds):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid and win32gui.IsWindowVisible(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # คืนค่าจาก Minimized
                win32gui.SetForegroundWindow(hwnd)  # นำหน้าต่างขึ้นมา
                hwnds.append(hwnd)
            return True
        
        hwnds = []
        win32gui.EnumWindows(callback, hwnds)

        if hwnds:
            print("✅ Found existing window and brought it to foreground")
            return True
        else:
            print("⚠️ No existing window found")
            return False

    def register_taskbar_restart(self):
        """ลงทะเบียน taskbar handler ให้รองรับการเปิดจาก Taskbar"""
        try:
            self.hwnd = self.winfo_id()

            # โหลดฟังก์ชัน SetWindowSubclass จาก comctl32.dll
            comctl32 = ctypes.WinDLL("comctl32")
            SetWindowSubclass = comctl32.SetWindowSubclass
            SetWindowSubclass.argtypes = [wintypes.HWND, wintypes.LPVOID, wintypes.UINT_PTR, wintypes.DWORD]
            SetWindowSubclass.restype = wintypes.BOOL

            # กำหนด callback ให้กับ WNDPROC
            self.WNDPROC = ctypes.WINFUNCTYPE(wintypes.LRESULT, wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)(self.wnd_proc)
            
            # ลงทะเบียน subclass
            if not SetWindowSubclass(self.hwnd, self.WNDPROC, 0, 0):
                raise ctypes.WinError()
            
            print("✅ Taskbar restart handler registered successfully")
        except Exception as e:
            print(f"❌ ไม่สามารถลงทะเบียน taskbar handler: {e}")

    def wnd_proc(self, hwnd, msg, wparam, lparam):
        """Windows callback handler สำหรับการจัดการข้อความจาก Taskbar"""
        if msg == win32con.WM_ACTIVATEAPP and wparam:
            self.after(100, self.show_window)

        # ใช้ DefWindowProc() แทน CallWindowProc()
        return ctypes.windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam)
    
    def on_taskbar_click(self, event=None):
        """จัดการเมื่อคลิกที่ไอคอนใน Taskbar"""
        if not self.winfo_viewable():  # ถ้าหน้าต่างถูกซ่อนอยู่
            self.show_window()
        return "break"
def open_login():
    """ เปิด Login.exe หรือ Login.py ใหม่ """
    try:
        # ตรวจสอบว่ารันจาก .exe หรือไม่
        if getattr(sys, 'frozen', False):  # ถ้าเป็น .exe
            base_dir = sys._MEIPASS  # PyInstaller แตกไฟล์ไว้ที่นี่
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))  # ถ้ารันจาก .py

        # กำหนดพาธที่เป็นไปได้ของ Login.py และ Login.exe
        login_py_path = os.path.join(base_dir, "Login.py")
        login_exe_path = os.path.join(base_dir, "Login.exe")

        # ตรวจสอบว่า Login.exe มีอยู่หรือไม่
        if os.path.exists(login_exe_path):
            subprocess.Popen([login_exe_path], shell=True)  # เปิด Login.exe
        elif os.path.exists(login_py_path):
            subprocess.Popen([sys.executable, login_py_path], shell=True)  # เปิด Login.py
        else:
            messagebox.showerror("Error", f"Cannot find Login.py or Login.exe at {base_dir}")
            return

        print("✅ Login เปิดสำเร็จ! ปิดโปรแกรมปัจจุบัน")
        
        quit()  # ปิด Tkinter mainloop
        after(500, lambda: sys.exit(0))  # รอ 0.5 วินาทีแล้วค่อยปิดโปรแกรม
    except Exception as e:
        messagebox.showerror("Error", f"Failed to restart Login: {e}")



if __name__ == "__main__":
    # ใช้ Mutex เพื่อป้องกันการเปิดซ้ำ
    mutex_name = "ERGO_PROJECT_MUTEX"
    mutex = win32event.CreateMutex(None, 1, mutex_name)
    last_error = win32api.GetLastError()

    app_instance = App("dummy@email.com")  # สร้างอินสแตนซ์เพื่อตรวจสอบ

    if last_error == winerror.ERROR_ALREADY_EXISTS or app_instance.is_already_running():
        print("⚠️ โปรแกรมกำลังทำงานอยู่แล้ว จะแสดงหน้าต่างที่มีอยู่แทน")
        sys.exit(0)

    if len(sys.argv) > 1:
        user_email = sys.argv[1]  # ✅ ดึง email จาก arguments
        app = App(user_email)
        app.mainloop()
    else:
        open_login()
        print("Error: No user email provided.")