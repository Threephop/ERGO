import os
import tkinter as tk
from tkinter import ttk
from azure.storage.blob import BlobServiceClient
from video_player import play_video  # ฟังก์ชันเล่นวิดีโอ

# ตรวจสอบพาธเต็ม
video_folder = os.path.join(os.path.dirname(__file__), "video")
updated_videos_folder = os.path.join(video_folder, "updated_videos")
print(f"🛠️ Full path to video folder: {os.path.abspath(video_folder)}")
print(f"🛠️ Full path to updated_videos folder: {os.path.abspath(updated_videos_folder)}")

# 🔹 ตั้งค่าการเชื่อมต่อ Azure
AZURE_CONNECTION_STRING = "Connection string here"
CONTAINER_NAME = "ergodefault"

blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

blobs = [blob.name for blob in container_client.list_blobs()]
print("📜 Files in Azure Blob Storage:", blobs)

# 🔹 กำหนดโฟลเดอร์วิดีโอ
DEFAULT_VIDEO_DIR = os.path.join(os.path.dirname(__file__), "video", "default_videos")
UPDATED_VIDEO_DIR = os.path.join(os.path.dirname(__file__), "video", "updated_videos")

class HomeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        """สร้าง UI"""
        self.pack(fill=tk.BOTH, expand=True)
        
        # ปุ่มอัปเดตวิดีโอ
        self.update_button = tk.Button(self, text="🔄 Update Videos", command=self.update_videos)
        self.update_button.pack(pady=5)

        # Combobox รายการวิดีโอ
        self.video_list = ttk.Combobox(self, state="readonly")
        self.video_list.pack(pady=5)
        self.load_video_list()

        # ปุ่มเล่นวิดีโอ
        self.play_button = tk.Button(self, text="▶️ Play Video", command=self.play_selected_video)
        self.play_button.pack(pady=5)

    def download_videos(self):
        """ดาวน์โหลดวิดีโอจาก Azure"""
        # สร้างโฟลเดอร์หลัก (`video`) ถ้ายังไม่มี
        video_folder = os.path.join(os.path.dirname(__file__), "video")
        if not os.path.exists(video_folder):
            os.makedirs(video_folder)
            print(f"📂 Created folder: {video_folder}")

        # สร้างโฟลเดอร์ `updated_videos` ถ้ายังไม่มี
        update_videos_folder = os.path.join(video_folder, "updated_videos")
        if not os.path.exists(update_videos_folder):
            os.makedirs(update_videos_folder)
            print(f"📂 Created folder: {update_videos_folder}")

        blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        blobs = [blob.name for blob in container_client.list_blobs()]

        for blob_name in blobs:
            # ใช้ os.path.join เพื่อสร้างพาธไฟล์
            local_file_path = os.path.join(update_videos_folder, os.path.basename(blob_name))
            print(f"📌 Trying to download: {blob_name} → {local_file_path}")

            if not os.path.exists(local_file_path):  
                try:
                    with open(local_file_path, "wb") as file:
                        download_stream = container_client.download_blob(blob_name)
                        file.write(download_stream.readall())

                    print(f"✅ Downloaded: {blob_name}")
                except Exception as e:
                    print(f"❌ Failed to download {blob_name}: {e}")
            else:
                print(f"✅ Already exists: {blob_name}")
                
    def load_video_list(self):
        """โหลดรายการวิดีโอที่มีใน local"""
        videos = []

        for folder in [DEFAULT_VIDEO_DIR, UPDATED_VIDEO_DIR]:
            if os.path.exists(folder):
                videos.extend([f for f in os.listdir(folder) if f.endswith((".mp4", ".avi"))])

        # อัปเดต Combobox แสดงเฉพาะชื่อไฟล์ ไม่ใช้พาธเต็ม
        self.video_list["values"] = videos
        if videos:
            self.video_list.current(0)  # เลือกวิดีโอตัวแรก
        print(f"📜 Loaded videos: {videos}")

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
            play_video(video_path)
        else:
            print(f"❌ Error: Video file not found - {selected_video}")

    def update_videos(self):
        """อัปเดตวิดีโอจาก Azure"""
        self.download_videos()
        self.load_video_list()  # รีเฟรชรายการวิดีโอหลังจากอัปเดต
        print("✅ Videos updated!")

# 🔹 สร้างหน้าต่างหลัก
if __name__ == "__main__":
    root = tk.Tk()
    root.title("🎬 Video Player with Azure Update")
    root.geometry("400x250")  # ตั้งค่าขนาดหน้าต่าง
    app = HomeFrame(root)
    root.mainloop()