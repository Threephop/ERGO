import cv2
from tkinter import messagebox
import os
from video_player import play_video # ฟังก์ชันเล่นวิดีโอ

# 🔹 กำหนดโฟลเดอร์วิดีโอ
DEFAULT_VIDEO_DIR = os.path.join(os.path.dirname(__file__), "video", "default_videos")
UPDATED_VIDEO_DIR = os.path.join(os.path.dirname(__file__), "video", "updated_videos")

def get_video_list():
    """โหลดวิดีโอจากโฟลเดอร์ DEFAULT และ UPDATED"""
    video_files = {}
    
    # ✅ ค้นหาวิดีโอในทั้งสองโฟลเดอร์
    for folder in [DEFAULT_VIDEO_DIR, UPDATED_VIDEO_DIR]:
        if os.path.exists(folder):
            for file in os.listdir(folder):
                if file.endswith(('.mp4', '.avi')):
                    video_files[file] = os.path.join(folder, file)
    
    return video_files

def show_popup():
    from tkinter import Toplevel, StringVar, ttk, Button

    popup = Toplevel()
    popup.title("เลือกวิดีโอ")
    popup.geometry("300x200")

    video_list = get_video_list()

    def select_video():
        selected = video_var.get()
        if selected and selected in video_list:
            print(f"Selected video: {selected}")
            play_video(video_list[selected])
        else:
            messagebox.showerror("Error", "กรุณาเลือกวิดีโอ")

    # Dropdown ให้เลือกวิดีโอ
    video_var = StringVar(value=list(video_list.keys())[0])
    ttk.Label(popup, text="เลือกวิดีโอ").pack(pady=10)
    video_dropdown = ttk.Combobox(popup, textvariable=video_var, values=list(video_list.keys()), state="readonly")
    video_dropdown.pack(pady=10)

    Button(popup, text="เล่นวิดีโอ", command=select_video).pack(pady=10)
