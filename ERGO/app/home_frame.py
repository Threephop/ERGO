import os
import tkinter as tk
from tkinter import ttk, Canvas, Scrollbar
from PIL import Image, ImageTk
import cv2  # ใช้สำหรับดึงเฟรมแรกของวิดีโอ
from video_player import play_video  # ฟังก์ชันเล่นวิดีโอ
import customtkinter as ctk  # ใช้ CustomTkinter
import requests

API_BASE_URL = "http://localhost:8000"  # URL ของ FastAPI
# ตรวจสอบพาธเต็ม
video_folder = os.path.join(os.path.dirname(__file__), "video")
updated_videos_folder = os.path.join(video_folder, "updated_videos")
print(f"\U0001F6E0️ Full path to video folder: {os.path.abspath(video_folder)}")
print(f"\U0001F6E0️ Full path to updated_videos folder: {os.path.abspath(updated_videos_folder)}")

# 🔹 กำหนดโฟลเดอร์วิดีโอ
DEFAULT_VIDEO_DIR = os.path.join(os.path.dirname(__file__), "video", "default_videos")
UPDATED_VIDEO_DIR = os.path.join(os.path.dirname(__file__), "video", "updated_videos")
THUMBNAIL_SIZE = (250, 200)  # กำหนดขนาด Thumbnail
ctk.set_appearance_mode("light")

def open_video_player(video_path):
    root = tk.Toplevel()  # สร้างหน้าต่างใหม่
    player = VideoPlayer(root, video_path)  # สร้าง VideoPlayer และส่ง root กับ video_path เข้าไป
    
class HomeFrame(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="white") 
        self.parent = parent
        self.columns = max(3, self.winfo_width() // 250)  # ✅ ปรับค่าเริ่มต้น
        self.init_ui()
        self.bind("<Configure>", self.on_resize)  # ตรวจจับการเปลี่ยนขนาดหน้าต่าง

        self.after(100, lambda: self.on_resize(None)) # ✅ เรียก on_resize() ตั้งแต่แรก


    def init_ui(self):
        """สร้าง UI ใหม่ พร้อมปรับดีไซน์ปุ่ม"""
        self.pack(fill=tk.BOTH, expand=True)
        
        # 🔹 ปุ่ม Update Videos (ไว้ด้านขวา)
        self.update_button = ctk.CTkButton(
            self, text="\U0001F504 Update Videos", 
            command=self.update_videos, fg_color="#007BFF", hover_color="#0056b3"
        )
        self.update_button.pack(pady=5, padx=10, anchor="e")  # ชิดขวา

        # 🔹 สร้าง Scrollable Frame
        self.canvas = tk.Canvas(self, bg="white")  
        self.scroll_y = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.frame = ctk.CTkFrame(self.canvas, fg_color="white")  

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll_y.set)

        self.scroll_y.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)  # เมาส์เลื่อน Scroll

        self.load_video_list()
        
    def get_video_thumbnail(self, video_path):
        """ดึง Thumbnail ของวิดีโอ (เฟรมแรก)"""
        cap = cv2.VideoCapture(video_path, cv2.CAP_FFMPEG)
        ret, frame = cap.read()
        cap.release()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            image.thumbnail(THUMBNAIL_SIZE)
            return ImageTk.PhotoImage(image)
        return None
        
    def download_videos_from_azure(self):
        """เรียก API เพื่อดึง URL วิดีโอจาก list_videos แล้วดาวน์โหลดลงโฟลเดอร์"""
        if not os.path.exists(UPDATED_VIDEO_DIR):
            os.makedirs(UPDATED_VIDEO_DIR)

        try:
            # เรียก API /list_videos เพื่อดึงรายการวิดีโอ
            response = requests.get(f"{API_BASE_URL}/list_videos/")
            if response.status_code == 200:
                posts = response.json()  # posts เป็น dictionary ที่มี key "videos"
                
                for post in posts["videos"]:  # ใช้ posts["videos"] เพื่อเข้าถึงรายการวิดีโอ
                    video_url = post.get("url")  # ใช้ key "url" ตาม JSON ที่ได้
                    if not video_url:
                        continue

                    file_name = os.path.basename(video_url)
                    local_file_path = os.path.join(UPDATED_VIDEO_DIR, file_name)

                    if not os.path.exists(local_file_path):
                        # ดาวน์โหลดวิดีโอจาก URL
                        download_response = requests.get(video_url, stream=True)
                        if download_response.status_code == 200:
                            with open(local_file_path, "wb") as f:
                                for chunk in download_response.iter_content(1024):
                                    f.write(chunk)
                            print(f"✅ Downloaded: {file_name}")
                        else:
                            print(f"❌ Failed to download {file_name}")
                    else:
                        print(f"✅ Already exists: {file_name}")

            else:
                print("❌ Failed to fetch video list from API")
        except Exception as e:
            print(f"❌ API Request Error: {e}")

            
    def load_video_list(self):
        """โหลดรายการวิดีโอและแสดงเป็น Thumbnail Grid"""
        for widget in self.frame.winfo_children():
            widget.destroy()

        videos = []
        for folder in [DEFAULT_VIDEO_DIR, UPDATED_VIDEO_DIR]:
            if os.path.exists(folder):
                videos.extend([os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(('.mp4', '.avi'))])

        self.video_thumbnails = []

        for idx, video_path in enumerate(videos):
            thumbnail = self.get_video_thumbnail(video_path)
            if thumbnail:
                self.video_thumbnails.append(thumbnail)

                frame = ctk.CTkFrame(self.frame, corner_radius=10)  
                frame.grid(row=idx // self.columns, column=idx % self.columns, padx=15, pady=15)

                label = tk.Label(frame, image=thumbnail)
                label.pack()

                btn = ctk.CTkButton(
                    frame, text=os.path.basename(video_path), 
                    command=lambda v=video_path: open_video_player(v), 
                    fg_color="#28A745", hover_color="#1E7E34"
                )
                btn.pack(pady=5)

        self.frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))        
    
    def play_selected_video(self):
        """เล่นวิดีโอที่เลือก"""
        selected_video = self.video_list.get()
        if not selected_video:
            return

        # ค้นหาวิดีโอจากโฟลเดอร์ที่ถูกต้อง
        video_path = os.path.join(DEFAULT_VIDEO_DIR, selected_video)
        if not os.path.exists(video_path):
            video_path = os.path.join(UPDATED_VIDEO_DIR, selected_video)

        if os.path.exists(video_path):
            # Ensure previous video is paused/stopped before opening new one
            open_video_player(video_path)
        else:
            print(f"❌ Error: Video file not found - {selected_video}")

    def on_resize(self, event=None):
        if event is None:
            width, height = self.winfo_width(), self.winfo_height()
        else:
            width, height = event.width, event.height

        """ตรวจจับการเปลี่ยนขนาดหน้าต่างแล้วปรับจำนวนวิดีโอต่อแถว"""
        if event:
            width = event.width
        else:
            width = self.winfo_width()  # ใช้ความกว้างของ widget ถ้าไม่มี event
        self.columns = max(2, width // 250)  # ปรับจำนวนวิดีโอต่อแถวอัตโนมัติ
        self.load_video_list()

    def on_mouse_wheel(self, event):
        """ให้ Canvas ใช้เมาส์เลื่อน Scroll ได้"""
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")


    def update_videos(self):
        """อัปเดตวิดีโอจาก Azure"""
        print("🔄 Downloading videos from Azure...")
        self.download_videos_from_azure()
        self.load_video_list()
        print("✅ Videos updated!")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("🎬 Video Player with Azure Update")
    root.geometry("400x250")  # ตั้งค่าขนาดหน้าต่าง
    app = HomeFrame(root)
    root.mainloop()

