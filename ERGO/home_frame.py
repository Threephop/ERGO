import tkinter as tk
from tkinter import PhotoImage
import subprocess  # สำหรับเปิดวิดีโอในโปรแกรมภายนอก

class HomeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")

        # Title
        tk.Label(self, text="Title", bg="#ffffff", fg="#000000", font=("Arial", 24)).pack(pady=10)

        # Video Section
        video_data = [
            {"title": "Sample Video", 
             "image": "path_to_thumbnail.png", 
             "path": r"C:\Users\User\Downloads\SampleVideo_1280x720_1mb.mp4",
             "description": "ตัวอย่างวิดีโอ"}
        ]

        # Grid layout for video
        video_frame = tk.Frame(self, bg="#ffffff")
        video_frame.pack(pady=10)

        for i, video in enumerate(video_data):
            # Placeholder image for video thumbnail
            thumbnail = PhotoImage(file="")  # เปลี่ยน path ให้เป็นภาพจริง
            video_btn = tk.Button(video_frame, image=thumbnail, text=video["description"],
                                   compound="top", bg="#ffffff", fg="#000000",
                                   command=lambda v=video: self.play_video(v))
            video_btn.image = thumbnail  # เก็บ reference เพื่อป้องกัน garbage collection
            video_btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)

    def play_video(self, video):
        # ใช้ subprocess เปิดวิดีโอในโปรแกรมเล่นวิดีโอ
        video_path = video['path']
        print(f"Playing video: {video['title']} at {video_path}")
        subprocess.run(["vlc", video_path])  # แก้ "vlc" เป็นโปรแกรมเล่นวิดีโอในระบบของคุณ เช่น "C:/Program Files/VLC/vlc.exe"

if __name__ == "__main__":
    root = tk.Tk()
    root.title("ERGO PROJECT")
    root.geometry("800x600")
    HomeFrame(root).pack(expand=True, fill="both")
    root.mainloop()
