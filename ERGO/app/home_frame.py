import tkinter as tk
from tkinter import PhotoImage, messagebox
import os  # For opening local video files
import cv2  # For playing video using OpenCV
import threading  # For running video playback in a separate thread

# Video Section
video_dir = os.path.join(os.path.dirname(__file__), "video")
video1_path = os.path.join(video_dir, "video1.mp4")
icon_dir = os.path.join(os.path.dirname(__file__), "icon")
video1_icon_path = os.path.join(icon_dir, "video1.png")

# Video Section
video_data = [
    {"title": "Video Name + 500 K.cal", "path": video1_path, "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP1", "image": video1_icon_path},
    {"title": "Video Name", "path": video1_path, "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP2", "image": video1_icon_path},
    {"title": "Video Name", "path": video1_path, "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP3", "image": video1_icon_path},
    {"title": "Video Name", "path": video1_path, "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP4", "image": video1_icon_path},
    {"title": "Video Name", "path": video1_path, "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP5", "image": video1_icon_path}
]


video_playing = False

class HomeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")

        # Main content
        main_content = tk.Frame(self, bg="#ffffff")
        main_content.pack(side="right", expand=True, fill="both")

        # Title
        tk.Label(main_content, text="Video", bg="#ffffff", fg="#000000", font=("PTT 45 Pride", 24, "bold")).pack(pady=10)
        tk.Label(main_content, text="วิดีโอสุขภาพ", 
                 bg="#ffffff", fg="#888888", font=("PTT 45 Pride", 12, "italic")).pack(pady=5)

        video_frame = tk.Frame(main_content, bg="#ffffff")
        video_frame.pack(pady=10)

        for i, video in enumerate(video_data):
            try:
                thumbnail = PhotoImage(file=video["image"]).subsample(2, 2)  # Load image and resize
            except Exception as e:
                print(f"Error loading image for {video['title']}: {e}")
                thumbnail = PhotoImage(width=150, height=100)  # Placeholder image

            video_btn = tk.Button(video_frame, image=thumbnail, text=video["description"],
                                   compound="top", bg="#ffffff", fg="#000000",
                                   font=("PTT 45 Pride", 10),
                                   command=lambda v=video: self.play_video(v["path"]))
            video_btn.image = thumbnail  # Keep a reference to prevent garbage collection
            video_btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)

    def play_video(self, video_path):
        def run_video():
            global video_playing
            video_playing = True

            cap = cv2.VideoCapture(video_path)

            if not cap.isOpened():
                messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถเปิดวิดีโอได้")
                return
            
            window_name = "Video Player"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            
            while video_playing and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                cv2.imshow(window_name, frame)

                key = cv2.waitKey(25)
                if key == ord('q') or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break

            cap.release()
            cv2.destroyAllWindows()  # แก้ไขตรงนี้
            video_playing = False

        threading.Thread(target=run_video, daemon=True).start()  # ใช้ daemon=True ให้ปิด thread อัตโนมัติ
