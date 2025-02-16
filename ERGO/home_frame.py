import tkinter as tk
<<<<<<< HEAD
from tkinter import PhotoImage, messagebox
import os  # For opening local video files
import cv2  # For playing video using OpenCV
import threading  # For running video playback in a separate thread

# Video Section
video_data = [
    {"title": "Video Name + นอก K.cal", "path": "C:\\Users\\User\\Downloads\\video1.mp4", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP1", "image": "C:\\Users\\User\\Downloads\\image111111.png"},
    {"title": "Video Name", "path": "C:\\Users\\User\\Downloads\\video2.mp4", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP2", "image": "C:\\Users\\User\\Downloads\\image111111.png"},
    {"title": "Video Name", "path":"C:\\Users\\User\\Downloads\\VideoTest\\sample-mp4-files-sample_640x360.mp4", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP3", "image": "C:\\Users\\User\\Downloads\\image111111.png"},
    {"title": "Video Name", "path": "C:\\Users\\User\\Downloads\\VideoTest\\SampleVideo_1280x720_1mb.mp4", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP4", "image": "C:\\Users\\User\\Downloads\\image111111.png"},
    {"title": "Video Name", "path": "C:\\Users\\User\\Downloads\\Video5.mp4", "description": "\u0e04\u0e33\u0e2d\u0e34\u0e19\u0e22\u0e32\u0e1a\u0e23\u0e34\u0e2b\u0e32\u0e23\u0e2a\u0e48\u0e27\u0e19 EP5", "image": "C:\\Users\\User\\Downloads\\image111111.png"}
]


video_playing = False
=======
from ffpyplayer.player import MediaPlayer
import cv2
from PIL import Image, ImageTk
import threading
>>>>>>> 5b0e05826978a165422bfcb703b9c0517a65d461

class HomeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")
<<<<<<< HEAD

        # Main content
        main_content = tk.Frame(self, bg="#ffffff")
        main_content.pack(side="right", expand=True, fill="both")

        # Title
        tk.Label(main_content, text="Video", bg="#ffffff", fg="#000000", font=("Arial", 24, "bold")).pack(pady=10)
        tk.Label(main_content, text="วิดีโอสุขภาพ", 
                 bg="#ffffff", fg="#888888", font=("Arial", 12, "italic")).pack(pady=5)

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
                                   font=("Arial", 10),
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

            while video_playing and cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break

                cv2.imshow("เล่นวิดีโอ (ปิดหน้าต่างเพื่อหยุด)", frame)
                if cv2.getWindowProperty("เล่นวิดีโอ (ปิดหน้าต่างเพื่อหยุด)", cv2.WND_PROP_VISIBLE) < 1:
                    break

                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()
            video_playing = False

        threading.Thread(target=run_video).start()

=======
        
        # กำหนดขนาดหน้าต่าง
        parent.geometry("1024x768")
        
        # Label สำหรับหน้าหลัก
        label = tk.Label(self, text="Home Page", bg="#ffffff", fg="#000000", font=("Arial", 24))
        label.pack(pady=20)
        
        # สร้างตัวแสดงวิดีโอ
        self.video_label = tk.Label(self)
        self.video_label.pack(pady=10)
        
        # ปุ่ม Play/Pause
        self.play_button = tk.Button(self, text="Play", command=self.toggle_video)
        self.play_button.pack(pady=10)

        # URL ของวิดีโอ
        self.video_url = "https://ergoproject.blob.core.windows.net/ergovideo/videoplayback.mp4"
        
        # สถานะการเล่น
        self.is_playing = False
        
        # ตัวแปรสำหรับการควบคุมกระบวนการ
        self.thread = None
        self.player = None

    def toggle_video(self):
        if self.is_playing:
            self.is_playing = False
            self.play_button.config(text="Play")
            if self.player:
                self.player.close()
        else:
            self.is_playing = True
            self.play_button.config(text="Pause")
            # เริ่มต้นกระบวนการเล่นวิดีโอใน Thread ใหม่
            self.thread = threading.Thread(target=self.play_video)
            self.thread.start()

    def play_video(self):
        self.player = MediaPlayer(self.video_url)

        while self.is_playing:
            grabbed, frame = self.player.get_frame()
            if not grabbed:
                break

            # แปลง frame จาก OpenCV (BGR) เป็น RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # แปลงภาพเป็นรูปที่สามารถแสดงใน Tkinter
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            # แสดงภาพบน label
            self.video_label.imgtk = imgtk
            self.video_label.configure(image=imgtk)

            # รอเวลาให้เหมาะสมสำหรับการแสดงภาพถัดไป
            cv2.waitKey(1)

        self.player.close()
>>>>>>> 5b0e05826978a165422bfcb703b9c0517a65d461
