import tkinter as tk
from home_frame import HomeFrame
from community_frame import CommunityFrame
from dashboard_frame import DashboardFrame
from leaderboard_frame import LeaderboardFrame
from setting_frame import SettingFrame
import os

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ERGO PROJECT")
        self.geometry("1024x768")  # ปรับขนาดหน้าต่าง
        self.configure(bg="white")  # สีพื้นหลังหน้าต่างหลัก

        # กำหนด path สำหรับไอคอนทั้งหมด
        self.icon_dir = os.path.join(os.path.dirname(__file__), "icon")

        # Sidebar
        self.sidebar = tk.Frame(self, bg="#221551", width=200)
        self.sidebar.pack(side="left", fill="y")

        self.frames = {}
        self.current_frame = None

        # Username Display with Profile Picture
        self.username_frame = tk.Frame(self.sidebar, bg="#221551", height=140)
        self.username_frame.pack(fill="x")

        # เพิ่มรูปโปรไฟล์
        profile_icon_path = os.path.join(self.icon_dir, "person_icon.png")
        profile_icon = tk.PhotoImage(file=profile_icon_path)
        profile_icon_label = tk.Label(self.username_frame, image=profile_icon, bg="#221551")
        profile_icon_label.image = profile_icon  # เก็บอ้างอิงเพื่อป้องกัน garbage collection
        profile_icon_label.pack(side="top", pady=10)  # ใช้ pady เพื่อจัดระยะห่างจากขอบบน

        # เพิ่มข้อความ Username
        tk.Label(self.username_frame, text="Username", font=("Arial", 14), fg="white", bg="#221551").pack(side="top", pady=10)

        # Sidebar buttons with icons
        self.create_sidebar_button("Home", HomeFrame, "home_icon.png")
        self.create_sidebar_button("Community", CommunityFrame, "community_icon.png")
        self.create_sidebar_button("Dashboard", DashboardFrame, "Dashboard_icon.png")
        self.create_sidebar_button("Leader-board", LeaderboardFrame, "Leaderboard_icon.png")

        # Add Setting button with place()
        # สร้างปุ่ม Setting
        setting_icon_path = os.path.join(self.icon_dir, "Settings_icon 1.png")
        setting_icon = tk.PhotoImage(file=setting_icon_path)

        self.setting_button = tk.Button(
            self.sidebar,
            image=setting_icon,
            compound="left",  # แสดงไอคอนทางซ้ายของข้อความ
            bg="#221551",
            fg="white",
            font=("Arial", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(SettingFrame),
        )
        self.setting_button.image = setting_icon  # เก็บอ้างอิงไอคอน
        self.setting_button.place(x=30, y=650)  # กำหนดตำแหน่งเริ่มต้น (เปลี่ยน x และ y ได้ตามต้องการ)

        # Default frame
        self.show_frame(HomeFrame)

    def create_sidebar_button(self, text, frame_class, icon_name):
        button_frame = tk.Frame(self.sidebar, bg="#221551")
        button_frame.pack(fill="x", pady=2)

        # ใช้ icon_name เพื่อให้แต่ละเมนูใช้ไอคอนที่แตกต่างกัน
        icon_path = os.path.join(self.icon_dir, icon_name)
        icon = tk.PhotoImage(file=icon_path)
        icon_label = tk.Label(button_frame, image=icon, bg="#221551")
        icon_label.image = icon  # เก็บอ้างอิงเพื่อป้องกัน garbage collection
        icon_label.pack(side="left", padx=10)

        button = tk.Button(
            button_frame,
            text=text,
            bg="#221551",
            fg="white",
            font=("Arial", 12),
            relief="flat",
            activebackground="#6F6969",
            activeforeground="white",
            command=lambda: self.show_frame(frame_class),
        )
        button.pack(side="left", fill="x", expand=True)

    def show_frame(self, frame_class):
        if self.current_frame:
            self.current_frame.pack_forget()
        if frame_class not in self.frames:
            self.frames[frame_class] = frame_class(self)
        self.current_frame = self.frames[frame_class]
        self.current_frame.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
