import tkinter as tk
from ffpyplayer.player import MediaPlayer
import cv2
from PIL import Image, ImageTk
import threading

class HomeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#ffffff")
        
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
