import tkinter as tk
from matplotlib import pyplot as plt
from home_frame import HomeFrame
from community_frame import CommunityFrame
from dashboard_frame import DashboardFrame
from leaderboard_frame import LeaderboardFrame
from setting_frame import SettingFrame
from PDPA_frame import PopupFrame
from profile_frame import ProfileFrame
import os
import requests

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ERGO PROJECT")
        self.geometry("1024x768")  # ขนาดหน้าต่าง
        self.configure(bg="white")  # สีพื้นหลังหน้าต่างหลัก
        window_width = 1024
        window_height = 768
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height / 2 - window_height / 2)
        position_right = int(screen_width / 2 - window_width / 2)
        self.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

        response = requests.get("http://127.0.0.1:8000/users")
        if response.status_code == 200:
            data = response.json()
            self.username = data['users'][3]
        
        self.show_popup()

        # กำหนด path สำหรับไอคอนทั้งหมด
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")
        
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
        self.sidebar.place(x=0, y=0)  # ใช้ place ให้ Sidebar อยู่ทางซ้ายสุด

        self.frames = {}
        self.current_frame = None

        # Username Display with Profile Picture
        self.username_frame = tk.Frame(self.sidebar, bg="#221551", height=200)
        self.username_frame.place(x=0, y=0, width=200)  # ใช้ place แทน pack

        # เพิ่มรูปโปรไฟล์
        profile_icon_path = os.path.join(self.icon_dir, "person_icon.png")
        profile_icon = tk.PhotoImage(file=profile_icon_path)
        profile_icon_label = tk.Label(self.username_frame, image=profile_icon, bg="#221551")
        profile_icon_label.image = profile_icon  # เก็บอ้างอิงเพื่อป้องกัน garbage collection
        profile_icon_label.place(x=60, y=10)  # ปรับตำแหน่งรูปโปรไฟล์

        # เพิ่มข้อความ Username
        tk.Label(self.username_frame, text=self.username, font=("PTT 45 Pride", 14), fg="white", bg="#221551").place(x=55, y=150)  # ปรับตำแหน่งข้อความ

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

        # สร้างปุ่ม Skip 1
        skipx1_icon_path = os.path.join(self.icon_dir, "skipx1.png")
        skipx1_icon = tk.PhotoImage(file=skipx1_icon_path)

        self.skipx1_button = tk.Button(
            self.sidebar,
            image=skipx1_icon,
            compound="left",  # แสดงไอคอนทางซ้ายของข้อความ
            bg="#221551",
            fg="white",
            font=("PTT 45 Pride", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
        )
        self.skipx1_button.image = skipx1_icon
        self.skipx1_button.place(x=45, y=700)  # ปรับตำแหน่งปุ่ม Skip 1

        # สร้างปุ่ม Skip 2
        skipx2_icon_path = os.path.join(self.icon_dir, "skipx2.png")
        skipx2_icon = tk.PhotoImage(file=skipx2_icon_path)

        self.skipx2_button = tk.Button(
            self.sidebar,
            image=skipx2_icon,
            compound="left",  # แสดงไอคอนทางซ้ายของข้อความ
            bg="#221551",
            fg="white",
            font=("PTT 45 Pride", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
        )
        self.skipx2_button.image = skipx2_icon
        self.skipx2_button.place(x=105, y=695)  # ปรับตำแหน่งปุ่ม Skip2
        self.speaker_button.place(x=104, y=641)  # ปรับตำแหน่งปุ่ม Skip2

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

    def toggle_mute(self):
        """สลับสถานะเสียงและอัปเดตไอคอนปุ่ม"""
        self.is_muted = not self.is_muted  # สลับสถานะ

        if self.is_muted:
            self.speaker_button.config(image=self.mute_icon)  # เปลี่ยนเป็นไอคอน mute
        else:
            self.speaker_button.config(image=self.speaker_icon)  # เปลี่ยนกลับเป็นไอคอน speaker

    def show_frame(self, frame_class):
        # ถ้าเฟรมที่ต้องการแสดงคือเฟรมเดียวกับที่แสดงอยู่แล้ว
        if self.current_frame and isinstance(self.current_frame, frame_class):
            return  # ไม่ต้องทำอะไร ถ้าเฟรมเดียวกัน
        
        # ซ่อนเฟรมปัจจุบัน
        if self.current_frame:
            self.current_frame.place_forget()  # ซ่อนเฟรมเก่า
        
        # สร้างเฟรมใหม่หากยังไม่มี
        if frame_class not in self.frames:
            if frame_class == SettingFrame:
                self.frames[frame_class] = frame_class(self, self.get_is_muted, self.on_language_change)

            else:
                self.frames[frame_class] = frame_class(self)
            if frame_class == SettingFrame:
                # ส่ง change_language_callback ไปให้ SettingFrame
                self.frames[frame_class] = frame_class(self, self.get_is_muted, self.on_language_change)
            else:
                self.frames[frame_class] = frame_class(self)
        
        # ตั้งค่าเฟรมใหม่เป็นเฟรมปัจจุบัน
        self.current_frame = self.frames[frame_class]
        
        # วางเฟรมใหม่
        self.current_frame.place(x=200, y=0, relwidth=1, relheight=1)

    def get_is_muted(self):
        """คืนค่าตัวแปร is_muted"""
        return self.is_muted

    def on_language_change(self, language):
        print(f"Language changed to: {language}")
        self.selected_language = language
        self.update_language(language)
    
    def show_popup(self):
        PopupFrame(self) 

    def on_closing(self):
        """Function to handle the window close event"""
        plt.close()  # ปิด figure ของ matplotlib
        self.quit()   # ปิดหน้าต่าง Tkinter
        
    def update_language(self, language):
        self.selected_language = language
        self.home_button.config(text=self.translations[self.selected_language]["home"])
        self.community_button.config(text=self.translations[self.selected_language]["community"])
        self.dashboard_button.config(text=self.translations[self.selected_language]["dashboard"])
        self.leaderboard_button.config(text=self.translations[self.selected_language]["leaderboard"])


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
